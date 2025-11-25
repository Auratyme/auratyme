"""
LLM Engine core class for schedule generation and refinement.

Orchestrates prompt building, LLM API calls, response parsing, and fallback
schedule generation when LLM calls fail. Supports multiple providers through
unified async/sync interfaces.

Educational Note:
    The LLMEngine follows the Facade pattern, providing a simple interface
    to complex LLM interactions while delegating provider-specific logic
    to specialized helper methods. This separation enables easy addition
    of new LLM providers without modifying core orchestration logic.
"""

import asyncio
import json5
import logging
import re
import time as time_module
from datetime import timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import jinja2
import requests

from .models import (
    ModelConfig,
    ModelProvider,
    ScheduleGenerationContext,
    Task,
    TaskPriority,
    EnergyLevel,
)
from .parser import extract_valid_json
from .templates import GENERATE_FROM_SCRATCH_TEMPLATE, REFINE_SCHEDULE_TEMPLATE
from src.core.solver.models import ScheduledTaskInfo

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    Engine for integrating LLMs into schedule optimization and refinement.
    
    Provides async/sync methods for generating schedules from scratch or
    refining solver-generated schedules using configurable LLM providers.
    
    Educational Note:
        Context manager support (__aenter__/__aexit__) ensures proper
        cleanup of aiohttp sessions, preventing resource leaks in long-running
        applications with many LLM calls.
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initializes LLMEngine with provider configuration.
        
        Args:
            config: ModelConfig instance with provider, API keys, and parameters
            
        Raises:
            TypeError: If config is not a ModelConfig instance
            
        Educational Note:
            Type checking at initialization provides clear error messages
            and prevents subtle bugs from incorrect configuration objects.
            Session management moved to per-call basis to prevent leaks.
        """
        if not isinstance(config, ModelConfig):
            raise TypeError("config must be an instance of ModelConfig")
            
        self.config = config
        self._prompt_template_from_scratch = GENERATE_FROM_SCRATCH_TEMPLATE
        self._prompt_template_refine = REFINE_SCHEDULE_TEMPLATE
        
        if not self._prompt_template_from_scratch or not self._prompt_template_refine:
            logger.error("One or more Jinja2 prompt templates failed to load")
            
        logger.info(f"LLMEngine initialized with {config.llm_provider.value} using {config.llm_model_name}")

    async def generate_schedule_from_scratch(
        self,
        context: ScheduleGenerationContext,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Generates complete schedule from user context without solver input.
        
        Deprecated in favor of refine_and_complete_schedule which uses
        constraint solver for hard requirements then LLM for soft optimization.
        """
        logger.warning("generate_schedule_from_scratch is deprecated. Use refine_and_complete_schedule")
        prompt = self._build_prompt(self._prompt_template_from_scratch, context, format_type)
        
        if not prompt:
            return self._generate_fallback_schedule(context, "Prompt template rendering failed")
            
        try:
            response = await self._call_llm_async(prompt)
            schedule = self._process_schedule_response(response, format_type)
            logger.info(f"Generated schedule from scratch for {context.user_name} on {context.target_date}")
            return schedule
        except Exception as e:
            logger.error(f"Error generating schedule from scratch: {e}", exc_info=True)
            return self._generate_fallback_schedule(context, str(e))

    async def refine_and_complete_schedule(
        self,
        solver_schedule: List[ScheduledTaskInfo],
        context: ScheduleGenerationContext,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Refines solver-generated skeleton schedule with human-friendly elements.
        
        Args:
            solver_schedule: Constraint-satisfying schedule from CP-SAT solver
            context: User profile, preferences, wearable data, etc.
            format_type: Response format ("json" or "text")
            
        Returns:
            Dict containing complete schedule with meals, breaks, activities
            
        Educational Note:
            Hybrid approach: solver ensures hard constraints (deadlines, sleep),
            LLM adds soft elements (meals, breaks, energy alignment) that require
            human judgment and context understanding.
        """
        import time
        refinement_start_time = time.time()
        
        logger.info(f"\n{'='*80}\n🎯 SCHEDULE REFINEMENT PIPELINE\n{'='*80}")
        logger.info(f"User: {context.user_name} | Date: {context.target_date}")
        
        logger.info(f"\n{'='*80}\n📥 INPUT DATA\n{'='*80}")
        logger.info(f"User: {context.user_name} | Date: {context.target_date}")
        
        if context.sleep_recommendation:
            logger.info(f"Sleep Window: {context.sleep_recommendation.ideal_bedtime.strftime('%H:%M')}-{context.sleep_recommendation.ideal_wake_time.strftime('%H:%M')}")
        
        logger.info(f"Fixed Events: {len(context.fixed_events)}")
        for idx, event in enumerate(context.fixed_events, 1):
            logger.info(f"  {idx}. {event.get('start_time')}-{event.get('end_time')}: {event.get('name')}")
        
        logger.info(f"Solver Schedule Items: {len(solver_schedule)}")
        for idx, item in enumerate(solver_schedule, 1):
            task_title = self._find_task_title(item.task_id, context.tasks)
            logger.info(f"  {idx}. {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}: {task_title}")
        logger.info(f"{'='*80}\n")
        
        self._last_solver_schedule = solver_schedule
        self._last_context = context
        
        prompt_start = time.time()
        prompt = self._build_prompt(
            self._prompt_template_refine,
            context,
            format_type,
            solver_schedule=solver_schedule
        )
        prompt_time = time.time() - prompt_start
        logger.info(f"✅ Prompt built in {prompt_time:.2f}s\n")
        
        if not prompt:
            return self._generate_fallback_schedule(context, "Prompt rendering failed in refinement")
            
        try:
            llm_start_time = time.time()
            
            response = await self._dispatch_provider_call(
                prompt,
                self.config.llm_temperature,
                self.config.llm_max_tokens
            )
            
            llm_elapsed = time.time() - llm_start_time
            logger.info(f"\n{'='*80}\n🔵 LLM RESPONSE PROCESSING (⏱️ {llm_elapsed:.2f}s)\n{'='*80}")
            logger.info(f"Response length: {len(response)} chars, ~{len(response.split())} words")
            logger.info(f"Response preview (first 250 chars): {response[:250]}...")
            logger.info(f"{'='*80}\n")
            
            parse_start = time.time()
            schedule = self._process_schedule_response(response, format_type)
            parse_time = time.time() - parse_start
            logger.info(f"✅ Response parsed in {parse_time:.2f}s")
            
            total_time = time.time() - refinement_start_time
            logger.info(f"\n{'='*80}\n📊 REFINEMENT SUMMARY\n{'='*80}")
            logger.info(f"Prompt building: {prompt_time:.2f}s ({prompt_time/total_time*100:.1f}%)")
            logger.info(f"LLM call: {llm_elapsed:.2f}s ({llm_elapsed/total_time*100:.1f}%)")
            logger.info(f"Response parsing: {parse_time:.2f}s ({parse_time/total_time*100:.1f}%)")
            logger.info(f"TOTAL TIME: {total_time:.2f}s")
            logger.info(f"✅ Successfully refined schedule for {context.user_name}")
            logger.info(f"{'='*80}\n")
            
            return schedule
            
        except Exception as e:
            elapsed = time.time() - refinement_start_time
            logger.error(f"❌ Error refining schedule after {elapsed:.2f}s: {e}", exc_info=True)
            return self._generate_fallback_schedule(context, str(e))

    async def _dispatch_provider_call(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Routes LLM call to appropriate provider-specific method.
        
        Educational Note:
            Strategy pattern implementation where provider enum acts as
            discriminator for selecting concrete API implementation.
        """
        import time
        provider = self.config.llm_provider
        
        logger.info(f"\n{'='*80}\n🔵 LLM REQUEST\n{'='*80}")
        logger.info(f"Provider: {provider.value} | Model: {self.config.llm_model_name}")
        logger.info(f"Temp: {temperature} | MaxTokens: {max_tokens} | Prompt: {len(prompt)} chars")
        logger.info(f"{'='*80}\n")
        
        start_time = time.time()
        
        if provider == ModelProvider.OPENAI:
            logger.info(f"⏳ Calling OpenAI async...")
            result = await self._call_openai_async(prompt, temperature, max_tokens)
        elif provider == ModelProvider.ANTHROPIC:
            logger.info(f"⏳ Calling Anthropic async...")
            result = await self._call_anthropic_async(prompt, temperature, max_tokens)
        elif provider == ModelProvider.MISTRAL:
            logger.info(f"⏳ Calling Mistral async...")
            result = await self._call_mistral_async(prompt, temperature, max_tokens)
        elif provider == ModelProvider.HUGGINGFACE:
            logger.info(f"⏳ Calling HuggingFace async...")
            result = await self._call_huggingface_async(prompt, temperature, max_tokens)
        elif provider == ModelProvider.OPENROUTER:
            logger.info(f"⏳ Calling OpenRouter async...")
            result = await self._call_openrouter_async(prompt, temperature, max_tokens)
        elif provider == ModelProvider.LOCAL:
            logger.info(f"⏳ Calling Local model...")
            result = self._call_local_model(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*80}\n⏱️  LLM TIMING\n{'='*80}")
        logger.info(f"Total time: {elapsed:.2f}s")
        logger.info(f"Response length: {len(result)} chars")
        logger.info(f"Average speed: {len(result)/elapsed:.0f} chars/sec")
        logger.info(f"{'='*80}\n")
        
        return result

    def generate_schedule_sync(
        self,
        context: ScheduleGenerationContext,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Synchronous schedule generation (deprecated).
        
        Educational Note:
            Sync methods maintained for backward compatibility but async
            versions preferred for better resource utilization in web servers.
        """
        logger.warning("generate_schedule_sync is deprecated. Use async refinement")
        prompt = self._build_prompt(self._prompt_template_from_scratch, context, format_type)
        
        if not prompt:
            return self._generate_fallback_schedule(context, "Prompt template rendering failed")
            
        try:
            response = self._call_llm_sync(prompt)
            schedule = self._process_schedule_response(response, format_type)
            logger.info(f"Generated schedule (sync) for {context.user_name}")
            return schedule
        except Exception as e:
            logger.error(f"Error generating schedule (sync): {e}", exc_info=True)
            return self._generate_fallback_schedule(context, str(e))

    async def explain_schedule_decision(
        self,
        schedule_item: Dict[str, Any],
        context: ScheduleGenerationContext
    ) -> str:
        """
        Generates natural language explanation for why item was scheduled at specific time.
        
        Educational Note:
            Explainability feature for user trust. Small prompt with low token
            limit keeps costs down while providing transparency.
        """
        item_type = schedule_item.get("type", "unknown")
        item_time_str = schedule_item.get("start_time", "")
        item_name = schedule_item.get("name", "")
        
        user_chronotype_str = (
            context.chronotype.value
            if context.chronotype
            else "Unknown"
        )
        
        prompt = f"""You are an AI assistant explaining schedule decisions.
Based on the user's data, explain why this item was scheduled at this time:

Item: {item_name}
Type: {item_type}
Scheduled Time: {item_time_str}

User Context:
- Chronotype: {user_chronotype_str}
- Energy: {self._get_energy_for_time(context.energy_pattern, item_time_str)}

Provide a brief explanation (under 50 words)."""
        
        try:
            response = await self._call_llm_async(prompt, temperature=0.5, max_tokens=100)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Could not generate explanation due to an error"

    async def adapt_from_feedback(
        self,
        previous_schedule: Dict[str, Any],
        feedback: Dict[str, Any],
        context: ScheduleGenerationContext
    ) -> Dict[str, Any]:
        """
        Adapts schedule generation based on user feedback.
        
        Educational Note:
            Learning from feedback loop. Additional context in prompt guides
            LLM to address specific user concerns in next iteration.
        """
        context.previous_feedback = feedback
        feedback_rating = feedback.get("rating", "N/A")
        feedback_text = feedback.get("comment", "No specific comments")
        
        prompt_addition = f"""IMPORTANT FEEDBACK (Rating: {feedback_rating}/5): "{feedback_text}"
Adjust the schedule to better address the user's concerns."""
        
        prompt = self._build_prompt(
            self._prompt_template_from_scratch,
            context,
            "json",
            additional_context=prompt_addition
        )
        
        if not prompt:
            return self._generate_fallback_schedule(context, "Prompt rendering failed during feedback adaptation")
            
        try:
            response = await self._call_llm_async(prompt)
            schedule = self._process_schedule_response(response, "json")
            logger.info(f"Adapted schedule based on feedback (Rating: {feedback_rating}/5)")
            return schedule
        except Exception as e:
            logger.error(f"Error adapting from feedback: {e}", exc_info=True)
            return self._generate_fallback_schedule(context, str(e))

    def _build_prompt(
        self,
        template: Optional[jinja2.Template],
        context: ScheduleGenerationContext,
        format_type: str = "json",
        additional_context: str = "",
        solver_schedule: Optional[List[ScheduledTaskInfo]] = None
    ) -> Optional[str]:
        """
        Renders Jinja2 template with context data to create LLM prompt.
        
        Educational Note:
            Template rendering separates prompt structure from data,
            enabling A/B testing and prompt evolution without code changes.
            
            Task names are enriched BEFORE rendering to ensure LLM receives
            human-readable names instead of UUIDs, improving prompt clarity
            and LLM understanding.
        """
        import time
        
        if template is None:
            logger.error("Cannot build prompt: Template is None")
            return None
        
        logger.info(f"\n{'='*80}\n📝 PROMPT BUILDING\n{'='*80}")
        build_start = time.time()
        
        enriched_solver_schedule = None
        if solver_schedule:
            enrich_start = time.time()
            enriched_solver_schedule = self._enrich_solver_schedule_with_names(
                solver_schedule, context.tasks
            )
            enrich_time = time.time() - enrich_start
            logger.info(f"✅ Enriched solver schedule ({len(enriched_solver_schedule)} items) in {enrich_time:.2f}s")
            
        template_context = {
            "user_id": context.user_id,
            "user_name": context.user_name,
            "target_date": context.target_date,
            "chronotype": context.chronotype,
            "prime_window": context.prime_window,
            "sleep_recommendation": context.sleep_recommendation,
            "tasks": context.tasks,
            "fixed_events": context.fixed_events,
            "preferences": context.preferences,
            "energy_pattern": context.energy_pattern,
            "wearable_insights": context.wearable_insights,
            "historical_insights": context.historical_insights,
            "rag_context": context.rag_context,
            "previous_feedback": context.previous_feedback,
            "additional_context": additional_context,
            "format_type": format_type,
            "solver_schedule": enriched_solver_schedule,
            "TaskPriority": TaskPriority,
            "EnergyLevel": EnergyLevel,
            "timedelta": timedelta
        }
        
        logger.info(f"Template context prepared: {len(template_context)} fields")
        
        try:
            render_start = time.time()
            prompt = template.render(template_context)
            render_time = time.time() - render_start
            
            logger.info(f"✅ Template rendered in {render_time:.2f}s")
            logger.info(f"Prompt size: {len(prompt)} chars, ~{len(prompt.split())} words")
            logger.info(f"Prompt preview (first 300 chars):\n{prompt[:300]}...")
            
            total_build_time = time.time() - build_start
            logger.info(f"📊 Total prompt build time: {total_build_time:.2f}s")
            logger.info(f"{'='*80}\n")
            
            return prompt.strip()
        except Exception as e:
            logger.exception("❌ Error rendering prompt template")
            return None
    
    def _enrich_solver_schedule_with_names(
        self,
        solver_schedule: List[ScheduledTaskInfo],
        tasks: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Enriches solver schedule items with task names.
        
        Educational Note:
            Converts solver output (task_id + timing) to LLM-friendly format
            by looking up human-readable task names. This prevents LLM from
            generating "Task UUID..." in final schedule.
        """
        enriched = []
        task_name_map = {str(task.id): task.title for task in tasks}
        
        for item in solver_schedule:
            task_name = task_name_map.get(str(item.task_id), f"Task {str(item.task_id)[:8]}")
            enriched.append({
                "task_id": str(item.task_id),
                "task_name": task_name,
                "start_time": item.start_time,
                "end_time": item.end_time
            })
        
        return enriched

    def _process_schedule_response(self, response: str, format_type: str) -> Dict[str, Any]:
        """
        Extracts and validates JSON schedule from LLM response.
        
        Educational Note:
            Robust parsing handles various LLM output formats (raw JSON,
            markdown-wrapped, text with JSON embedded) to maximize success rate.
        """
        if format_type == "json":
            logger.debug(f"Raw LLM response (first 500 chars): {response[:500]}...")
            
            try:
                json_str = extract_valid_json(response)
                logger.debug(f"Extracted JSON (first 500 chars): {json_str[:500]}...")
                
                schedule_data = json5.loads(json_str)
                
                if not isinstance(schedule_data, dict):
                    raise ValueError("Parsed JSON is not a dictionary")
                    
                if "schedule" not in schedule_data or not isinstance(schedule_data["schedule"], list):
                    raise ValueError("Invalid schedule format: missing or invalid 'schedule' array")
                
                sleep_count = sum(1 for item in schedule_data['schedule'] if item.get('type') == 'sleep')
                task_count = sum(1 for item in schedule_data['schedule'] if item.get('type') == 'task')
                
                if sleep_count == 0:
                    logger.error("❌ CRITICAL: No sleep items in schedule!")
                if task_count < len(getattr(self, '_last_solver_schedule', [])):
                    expected = len(getattr(self, '_last_solver_schedule', []))
                    logger.error(f"❌ CRITICAL: Missing tasks! Expected {expected}, got {task_count}")
                    
                return schedule_data
                
            except (ValueError, json5.JSONDecodeError) as e:
                logger.error(f"Failed to extract/parse JSON response: {e}")
                
                match = re.search(r"```json\s*([\s\S]*?)\s*```", response, re.IGNORECASE)
                if match:
                    logger.info("Found JSON in markdown block, attempting to parse")
                    try:
                        schedule_data = json5.loads(match.group(1))
                        if "schedule" in schedule_data and isinstance(schedule_data["schedule"], list):
                            return schedule_data
                        else:
                            raise ValueError("Markdown JSON missing 'schedule' array")
                    except (ValueError, json5.JSONDecodeError) as e_md:
                        logger.error(f"Markdown JSON parse failed: {e_md}")
                        
                logger.debug(f"Raw response: {response}")
                raise ValueError(f"Invalid or non-extractable JSON response: {e}")
                
            except Exception as e_gen:
                logger.error(f"Unexpected error processing JSON: {e_gen}", exc_info=True)
                raise ValueError(f"Unexpected error processing JSON: {e_gen}")
        else:
            return {"schedule_text": response.strip()}

    def _generate_fallback_schedule(
        self,
        context: ScheduleGenerationContext,
        error_message: str = "LLM generation failed"
    ) -> Dict[str, Any]:
        """
        Creates basic fallback schedule when LLM generation fails.
        
        Educational Note:
            Graceful degradation ensures users always get usable output
            even when LLM API is unavailable or returns invalid data.
        """
        logger.warning(f"Generating fallback schedule due to error: {error_message}")
        
        schedule_items = []
        
        for event in context.fixed_events:
            schedule_items.append({
                "type": "fixed_event",
                "name": event.get('name', 'Fixed Event'),
                "start_time": event.get('start_time', 'N/A'),
                "end_time": event.get('end_time', 'N/A'),
            })
            
        for task in context.tasks:
            schedule_items.append({
                "type": "task",
                "name": task.title,
                "start_time": "N/A",
                "end_time": "N/A",
                "task_id": str(task.id)
            })
            
        schedule_items.sort(key=lambda x: x.get('start_time', '99:99'))
        
        return {
            "schedule": schedule_items,
            "metrics": {"status": "fallback"},
            "explanations": {
                "error": f"Failed to generate optimized schedule: {error_message}. Displaying basic task list."
            },
            "warnings": [f"LLM generation failed: {error_message}"]
        }

    def _get_energy_for_time(self, energy_pattern: Optional[Dict[int, float]], time_str: str) -> str:
        """
        Converts energy pattern float to human-readable description.
        
        Educational Note:
            Helper for prompt building and explanations. Maps numerical
            energy levels to qualitative descriptions users understand.
        """
        if not energy_pattern or not time_str:
            return "Unknown"
            
        try:
            hour = int(time_str.split(':')[0])
            energy = energy_pattern.get(hour, 0.5)
            
            if energy >= 0.8:
                return f"High ({energy:.1f})"
            elif energy >= 0.4:
                return f"Medium ({energy:.1f})"
            else:
                return f"Low ({energy:.1f})"
                
        except (ValueError, IndexError):
            return "Unknown (invalid time)"

    async def _call_llm_async(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """
        Generic async LLM call dispatcher.
        
        Educational Note:
            Convenience method for simple prompts that don't need full
            schedule generation context. Used for explanations and adaptations.
        """
        temp = temperature if temperature is not None else self.config.llm_temperature
        tokens = max_tokens if max_tokens is not None else self.config.llm_max_tokens
        
        return await self._dispatch_provider_call(prompt, temp, tokens)

    def _call_llm_sync(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """Generic sync LLM call dispatcher (deprecated)."""
        raise NotImplementedError("Sync LLM calls not yet migrated to new structure")

    async def _call_llm_api(
        self,
        provider: ModelProvider,
        method: str,
        url: str,
        headers: Dict,
        payload: Dict
    ) -> Any:
        """
        Generic async HTTP API call with retry logic and error handling.
        
        Educational Note:
            Centralized retry logic with exponential backoff handles transient
            failures (rate limits, network issues) without manual intervention.
            Creates temporary session per call to prevent resource leaks.
        """
        import time
        
        async with aiohttp.ClientSession() as session:
            session_method = getattr(session, method.lower())
            
            for attempt in range(self.config.llm_max_retries + 1):
                try:
                    attempt_start = time.time()
                    logger.info(f"\n{'='*80}\n📡 HTTP API CALL (Attempt {attempt+1}/{self.config.llm_max_retries+1})\n{'='*80}")
                    logger.info(f"Method: {method} | URL: {url}")
                    logger.info(f"Timeout: {self.config.llm_request_timeout}s")
                    
                    auth_header = headers.get('Authorization', '')
                    if auth_header and auth_header.startswith('Bearer '):
                        masked_auth = f"Bearer {auth_header[7:30]}...{auth_header[-10:]}"
                        logger.info(f"🔑 Authorization header (masked): {masked_auth}")
                    else:
                        logger.info(f"❌ No valid Authorization header")
                    logger.debug(f"All headers: {headers}")
                    
                    async with session_method(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=self.config.llm_request_timeout
                    ) as response:
                        status = response.status
                        http_time = time.time() - attempt_start
                        
                        logger.info(f"✅ Received response (status {status}) in {http_time:.2f}s")
                        
                        if status == 401:
                            raise ValueError(f"{provider.value} API Authentication Error")
                        
                        if status == 429:
                            logger.warning(f"{provider.value} API rate limit exceeded, retrying...")
                            
                        elif status == 503 and provider == ModelProvider.HUGGINGFACE:
                            logger.warning("HuggingFace API is loading, waiting 15s...")
                            await asyncio.sleep(15)
                            continue
                            
                        elif status != 200:
                            error_text = await response.text()
                            logger.error(f"{provider.value} API error (status {status}): {error_text[:500]}...")
                            if attempt == self.config.llm_max_retries:
                                raise ValueError(f"{provider.value} API error after retries: {status}")
                        else:
                            if 'application/json' in response.headers.get('Content-Type', ''):
                                response_data = await response.json()
                            else:
                                response_data = await response.text()
                            
                            total_time = time.time() - attempt_start
                            logger.info(f"✅ Response parsed successfully in {total_time:.2f}s")
                            logger.info(f"{'='*80}\n")
                            return response_data
                                
                except (aiohttp.ClientError, ValueError, asyncio.TimeoutError) as e:
                    attempt_elapsed = time.time() - attempt_start
                    logger.warning(f"❌ Error during {provider.value} API call (attempt {attempt+1}, {attempt_elapsed:.2f}s): {e}")
                    if attempt == self.config.llm_max_retries:
                        raise
                        
                except Exception as e:
                    attempt_elapsed = time.time() - attempt_start
                    logger.exception(f"❌ Unexpected error during {provider.value} API call (attempt {attempt+1}, {attempt_elapsed:.2f}s)")
                    if attempt == self.config.llm_max_retries:
                        raise
                        
                if attempt < self.config.llm_max_retries:
                    wait_time = self.config.llm_retry_delay * (2 ** attempt)
                    logger.info(f"⏳ Waiting {wait_time:.1f}s before retry (exponential backoff)...")
                    await asyncio.sleep(wait_time)
                    
        logger.error(f"❌ {provider.value} API call failed after all retries")
        raise ValueError(f"{provider.value} API call failed after all retries")

    def _call_api_sync(
        self,
        provider: ModelProvider,
        method: str,
        url: str,
        headers: Dict,
        payload: Dict
    ) -> Any:
        """Generic sync HTTP API call with retry logic."""
        for attempt in range(self.config.llm_max_retries + 1):
            try:
                logger.debug(f"API Call Attempt {attempt+1}: {method} {url}")
                
                response = requests.request(
                    method,
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.config.llm_request_timeout
                )
                
                status = response.status_code
                logger.debug(f"API Response Status: {status}")
                
                if status == 401:
                    raise ValueError(f"{provider.value} API Authentication Error")
                    
                if status == 429:
                    logger.warning(f"{provider.value} API rate limit exceeded, retrying...")
                    
                elif status == 503 and provider == ModelProvider.HUGGINGFACE:
                    logger.warning("HuggingFace API is loading, waiting 15s...")
                    time_module.sleep(15)
                    continue
                    
                elif status != 200:
                    logger.error(f"{provider.value} API error (status {status}): {response.text[:500]}...")
                    if attempt == self.config.llm_max_retries:
                        raise ValueError(f"{provider.value} API error after retries: {status}")
                else:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        return response.json()
                    else:
                        return response.text
                        
            except (requests.RequestException, ValueError) as e:
                logger.warning(f"Error during {provider.value} API call (attempt {attempt+1}): {e}")
                if attempt == self.config.llm_max_retries:
                    raise
                    
            except Exception as e:
                logger.exception(f"Unexpected error during {provider.value} API call (attempt {attempt+1})")
                if attempt == self.config.llm_max_retries:
                    raise
                    
            if attempt < self.config.llm_max_retries:
                wait_time = self.config.llm_retry_delay * (2 ** attempt)
                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                time_module.sleep(wait_time)
                
        logger.error(f"{provider.value} API call failed after all retries")
        raise ValueError(f"{provider.value} API call failed after all retries")

    async def _call_openai_async(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """OpenAI API async call."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key missing")
        if not self.config.api_base:
            raise ValueError("OpenAI API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = f"{self.config.api_base}/chat/completions"
        
        try:
            result = await self._call_llm_api(ModelProvider.OPENAI, "POST", url, headers, payload)
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from OpenAI: {e}")
            raise ValueError("Invalid response structure from OpenAI") from e

    def _call_openai_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """OpenAI API sync call."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key missing")
        if not self.config.api_base:
            raise ValueError("OpenAI API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = f"{self.config.api_base}/chat/completions"
        
        try:
            result = self._call_api_sync(ModelProvider.OPENAI, "POST", url, headers, payload)
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from OpenAI: {e}")
            raise ValueError("Invalid response structure from OpenAI") from e

    async def _call_mistral_async(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Mistral API async call (uses OpenAI-compatible endpoint)."""
        return await self._call_openai_async(prompt, temperature, max_tokens)

    def _call_mistral_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Mistral API sync call (uses OpenAI-compatible endpoint)."""
        return self._call_openai_sync(prompt, temperature, max_tokens)

    async def _call_huggingface_async(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """HuggingFace API async call."""
        if not self.config.api_key:
            raise ValueError("HuggingFace API key missing")
        if not self.config.api_base:
            raise ValueError("HuggingFace API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": max(temperature, 0.01),
                "top_p": self.config.llm_top_p,
                "do_sample": True if temperature > 0 else False
            }
        }
        
        url = f"{self.config.api_base}/{self.config.llm_model_name}"
        
        try:
            result = await self._call_llm_api(ModelProvider.HUGGINGFACE, "POST", url, headers, payload)
            
            if isinstance(result, list) and result:
                return str(result[0].get("generated_text", result[0])).strip()
            if isinstance(result, dict):
                return str(result.get("generated_text", result)).strip()
            return str(result).strip()
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from HuggingFace: {e}")
            raise ValueError("Invalid response structure from HuggingFace") from e

    def _call_huggingface_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """HuggingFace API sync call."""
        if not self.config.api_key:
            raise ValueError("HuggingFace API key missing")
        if not self.config.api_base:
            raise ValueError("HuggingFace API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": max(temperature, 0.01),
                "top_p": self.config.llm_top_p,
                "do_sample": True if temperature > 0 else False
            }
        }
        
        url = f"{self.config.api_base}/{self.config.llm_model_name}"
        
        try:
            result = self._call_api_sync(ModelProvider.HUGGINGFACE, "POST", url, headers, payload)
            
            if isinstance(result, list) and result:
                return str(result[0].get("generated_text", result[0])).strip()
            if isinstance(result, dict):
                return str(result.get("generated_text", result)).strip()
            return str(result).strip()
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from HuggingFace: {e}")
            raise ValueError("Invalid response structure from HuggingFace") from e

    async def _call_anthropic_async(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Anthropic API async call."""
        if not self.config.api_key:
            raise ValueError("Anthropic API key missing")
        if not self.config.api_base:
            raise ValueError("Anthropic API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = f"{self.config.api_base}/messages"
        
        try:
            result = await self._call_llm_api(ModelProvider.ANTHROPIC, "POST", url, headers, payload)
            return result["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from Anthropic: {e}")
            raise ValueError("Invalid response structure from Anthropic") from e

    def _call_anthropic_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Anthropic API sync call."""
        if not self.config.api_key:
            raise ValueError("Anthropic API key missing")
        if not self.config.api_base:
            raise ValueError("Anthropic API base URL missing")
            
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = f"{self.config.api_base}/messages"
        
        try:
            result = self._call_api_sync(ModelProvider.ANTHROPIC, "POST", url, headers, payload)
            return result["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from Anthropic: {e}")
            raise ValueError("Invalid response structure from Anthropic") from e

    async def _call_openrouter_async(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """OpenRouter API async call with detailed timing and logging."""
        import time
        
        if not self.config.api_key:
            raise ValueError("OpenRouter API key missing")
        if not self.config.api_base:
            raise ValueError("OpenRouter API base URL missing")
        
        logger.info(f"\n{'='*80}\n🌐 OPENROUTER API CALL\n{'='*80}")
        logger.info(f"Endpoint: {self.config.api_base}/chat/completions")
        logger.info(f"Model: {self.config.llm_model_name}")
        logger.info(f"Parameters: temp={temperature}, max_tokens={max_tokens}, top_p={self.config.llm_top_p}")
        logger.info(f"🔑 API Key status: {'✅ Present' if self.config.api_key else '❌ Missing'}")
        logger.info(f"🔑 API Key length: {len(self.config.api_key) if self.config.api_key else 0}")
        logger.info(f"🔑 API Key preview: {self.config.api_key[:15]}...{self.config.api_key[-5:] if self.config.api_key else 'N/A'}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        logger.info(f"🔑 Authorization header (masked): Bearer {self.config.api_key[:20]}...{self.config.api_key[-10:]}")
        
        if self.config.llm_site_url:
            headers["HTTP-Referer"] = self.config.llm_site_url
            logger.info(f"Site URL: {self.config.llm_site_url}")
        if self.config.llm_site_name:
            headers["X-Title"] = self.config.llm_site_name
            logger.info(f"Site Name: {self.config.llm_site_name}")
            
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        logger.info(f"Payload size: {len(str(payload))} bytes")
        logger.info(f"Prompt length: {len(prompt)} chars, {len(prompt.split())} words")
        
        url = f"{self.config.api_base}/chat/completions"
        
        call_start_time = time.time()
        logger.info(f"📤 Sending request to OpenRouter...")
        
        try:
            result = await self._call_llm_api(ModelProvider.OPENROUTER, "POST", url, headers, payload)
            
            call_elapsed = time.time() - call_start_time
            logger.info(f"✅ Received response from OpenRouter in {call_elapsed:.2f}s")
            
            response_text = result["choices"][0]["message"]["content"]
            logger.info(f"📨 Response length: {len(response_text)} chars, {len(response_text.split())} words")
            
            if "usage" in result:
                usage = result["usage"]
                logger.info(f"📊 Token usage:")
                logger.info(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                logger.info(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                logger.info(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
            
            logger.info(f"Response preview: {response_text[:150]}...")
            logger.info(f"{'='*80}\n")
            
            return response_text
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from OpenRouter: {e}")
            logger.error(f"Response structure: {result}")
            raise ValueError("Invalid response structure from OpenRouter") from e
        except Exception as e:
            call_elapsed = time.time() - call_start_time
            logger.error(f"❌ OpenRouter call failed after {call_elapsed:.2f}s: {e}")
            raise

    def _call_openrouter_sync(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """OpenRouter API sync call."""
        if not self.config.api_key:
            raise ValueError("OpenRouter API key missing")
        if not self.config.api_base:
            raise ValueError("OpenRouter API base URL missing")
        
        logger.info(f"🔑 API Key status: {'✅ Present' if self.config.api_key else '❌ Missing'}")
        logger.info(f"🔑 API Key length: {len(self.config.api_key) if self.config.api_key else 0}")
        logger.info(f"🔑 API Key preview: {self.config.api_key[:15]}...{self.config.api_key[-5:] if self.config.api_key else 'N/A'}")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        if self.config.llm_site_url:
            headers["HTTP-Referer"] = self.config.llm_site_url
        if self.config.llm_site_name:
            headers["X-Title"] = self.config.llm_site_name
            
        payload = {
            "model": self.config.llm_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = f"{self.config.api_base}/chat/completions"
        
        try:
            result = self._call_api_sync(ModelProvider.OPENROUTER, "POST", url, headers, payload)
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response from OpenRouter: {e}")
            raise ValueError("Invalid response structure from OpenRouter") from e

    def _call_local_model(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Local model API call."""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": self.config.llm_top_p
        }
        
        url = self.config.api_base or "http://localhost:8000/v1/completions"
        logger.debug(f"Calling local model at: {url}")
        
        try:
            result = self._call_api_sync(ModelProvider.LOCAL, "POST", url, headers, payload)
            
            if isinstance(result, dict):
                return result.get("text", result.get("choices", [{}])[0].get("text", str(result)))
            return str(result)
            
        except Exception as e:
            logger.error(f"Error calling local model: {e}", exc_info=True)
            raise ValueError(f"Failed to get response from local model: {e}") from e

    def _find_task_title(self, task_id, tasks):
        """
        Finds task title by ID from task list.
        
        Educational Note:
            Handles both Task objects and dict representations for flexibility.
        """
        for task in tasks:
            if hasattr(task, 'id') and task.id == task_id:
                return getattr(task, 'title', 'Unknown Task')
            elif isinstance(task, dict) and task.get('id') == str(task_id):
                return task.get('title', task.get('name', 'Unknown Task'))
        return f"Task {str(task_id)[:8]}..."
