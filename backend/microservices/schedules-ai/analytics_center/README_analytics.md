# Analytics Control Center for Schedules-AI

**Competition-Ready Analytical Dashboard**

## Purpose
Professional UI for demonstrating AI-powered schedule generation with comprehensive analytics, chronotype-based optimization, and transparent decision-making. Designed for competition demos with one-click sample data and deep insights.

## Key Features
- **👤 User Profile Configuration**: Chronotype (MEQ), sleep needs, work preferences
- **📋 Task Management**: Priority-based task scheduling with fixed/flexible timing
- **⌚ Wearable Data Integration**: Sleep metrics, activity levels, recovery indicators
- **🚀 Real-time Schedule Generation**: Server-Sent Events (SSE) streaming
- **📊 Comprehensive Analytics**: Sleep calculations, energy alignment, task distribution
- **🧠 AI Decision Transparency**: Detailed explanations of scheduling choices
- **💾 Export Capabilities**: JSON, CSV downloads

## Competition Demo - One-Click Setup
```
pip install -r microservices/schedules-ai/core/requirements.txt
streamlit run microservices/schedules-ai/analytics_center/app/Main.py
```

Click "🎯 LOAD SAMPLE DATA" and everything is ready instantly!

### Sample Data Includes:
- **User**: Alex Johnson, 30, Tech industry, Intermediate chronotype (MEQ: 50)
- **Work**: Office 08:00-16:00, 30min commute
- **Tasks**: Code Review (50min), Documentation (110min), Bug Fix (50min), 1:1 Meeting (20min fixed)
- **Wearable**: Good sleep (7.5h), 8500 steps, 85% readiness
- **Preferences**: 45min lunch, 30min morning routine, 45min evening routine

## Comprehensive Analytics Dashboard

### 😴 Sleep & Recovery Analysis
- **Sleep Duration**: Calculated from schedule with cycle breakdown
- **Sleep Cycles**: 90-minute cycle counting (optimal: 4-6)
- **Chronotype Optimization**: Bedtime/wake time based on MEQ score
- **Scientific Rationale**: Detailed explanation of timing decisions

### ⚡ Energy & Productivity Metrics
- **Schedule Efficiency**: Time utilization percentage
- **Task Distribution**: Work vs. Personal vs. Routines
- **Flexibility Score**: Percentage of reschedulable tasks
- **Energy Alignment**: High-priority tasks during peak hours

### 🧠 AI Intelligence Transparency
Full explanation of scheduling decisions:
- Chronotype-aware task placement
- Priority-based optimization
- Break and recovery integration
- Work-life balance principles

## Architecture Overview
```
analytics_center/
  app/            # Streamlit entry + pages
  models/         # Pydantic schemas (UI, wearable)
  services/       # IO + ingestion + API + repairs pipeline
  utils/          # Pure helpers (validation, heuristics, timeline)
  tests/          # Focused unit tests
```

## Data Flow
Inputs (table) → Repair Pipeline → Payload Builder → API Client → Response → Timeline + KPIs → Heuristics (Explain) → Downloads.
Wearable: Uploaded File → Mapping → Raw Records → Feature Extraction (sleep, activity, steps, readiness) → CanonicalInput rows (Sleep/Activity) → Inputs Flow.

## Canonical Input Fields (summary)
- date, task_type, start_time, end_time, duration
- task_priority (1-5), breaks_count, breaks_duration
- energy_level, fatigue_level, motivation_level, mood
- fixed_task (True → fixed_events), efficiency_score
- rounding_flag (enables :00/:30 normalization)

## Repairs Pipeline
Order: enforce_rounding → fill_missing_end → clamp_day → shift_collisions.
Generated change log displayed for transparency.

## Heuristics (Fallback Explainability)
- utilization_ratio = scheduled_minutes / 1440
- prime_energy_alignment = fraction of high-energy tasks inside prime windows
- break_density = break_minutes / active_minutes
- rounding_compliance = fraction of times aligned to :00/:30

## Prime Energy Windows
Configurable list (default: 09:00–12:00, 14:00–17:00). Adjust via sidebar. Stored only in session.

## Wearable Extraction (MVP)
Mapping fields: sleep_start, sleep_end, sleep_quality, readiness_score, steps, activity_start, activity_end, activity_type.
Derived: total_sleep_minutes, main_sleep_window, steps_total, activity_blocks, stress_level (if mapped).
Sync adds Sleep (fixed) + Activity rows to Inputs.

## Demo Mode
If enabled: schedule synthesized deterministically from first tasks. Allows offline experimentation.

## Deep Internals (Planned)
Future: chronotype_profile, sleep_metrics, solver_input, core_schedule, llm_refinement_trace. Placeholder key: state.deep_internals.

## Testing
```
pytest -q
```
Key tests: validation, repairs, wearable ingestion. Add heuristics + client tests incrementally.

## Style & Quality
- Pydantic v2, type hints, single-responsibility helpers
- No hash comments; docstrings only
- Functions intentionally small for unit test coverage

## Limitations / Roadmap
- No real solver explanations surfaced yet
- No historical trend analytics (reserved)
- No live WebSocket streaming
- Activity classification naive (duration only)

## Educational Notes
This module isolates experimental analytics from production API, enabling safe iterative improvement of validation, feature engineering, and explainability models without destabilizing the core scheduling engine.

# Analytics Control Center (Skeleton)

Run:
```
streamlit run microservices/schedules-ai/analytics_center/app/Main.py
```
