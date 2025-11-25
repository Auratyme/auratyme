"""
JSON extraction and parsing utilities for LLM responses.

Provides robust extraction of JSON data from LLM-generated text that may contain
surrounding explanatory text, markdown code fences, or other formatting artifacts.

Educational Note:
    LLM responses are inherently unpredictable and may include extraneous text
    before/after the requested JSON. Robust parsing requires careful string
    scanning with proper quote/escape handling to avoid false bracket matches.
"""

import logging
import re

logger = logging.getLogger(__name__)


def find_json_start(text: str) -> tuple[int, str, str]:
    """
    Locates the starting position and type of JSON structure in text.
    
    Args:
        text: Raw LLM response text potentially containing JSON
        
    Returns:
        tuple: (start_index, open_char, close_char) e.g., (5, '{', '}')
        
    Raises:
        ValueError: If no JSON structure found
        
    Educational Note:
        JSON can start with either '{' (object) or '[' (array). Priority goes
        to whichever appears first to handle edge cases where both exist.
    """
    start_brace = text.find('{')
    start_bracket = text.find('[')
    
    if start_brace == -1 and start_bracket == -1:
        raise ValueError("No JSON object or array found in response")
        
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        return start_brace, '{', '}'
    else:
        return start_bracket, '[', ']'


def scan_for_balanced_close(text: str, start: int, open_char: str, close_char: str) -> int:
    """
    Scans text from start position to find matching closing bracket/brace.
    
    Args:
        text: Text to scan
        start: Starting position (index of opening char)
        open_char: Opening character ('{' or '[')
        close_char: Closing character ('}' or ']')
        
    Returns:
        int: Index of matching closing character
        
    Raises:
        ValueError: If no balanced closing character found
        
    Educational Note:
        State machine tracks nesting depth while respecting string boundaries
        and escape sequences. Critical for handling nested JSON with quoted brackets.
    """
    open_count = 0
    in_string = False
    escape = False
    
    for i in range(start, len(text)):
        char = text[i]
        
        if char == '"' and not escape:
            in_string = not in_string
        elif char == '\\' and not escape:
            escape = True
            continue
            
        if not in_string:
            if char == open_char:
                open_count += 1
            elif char == close_char:
                open_count -= 1
                if open_count == 0:
                    return i
                    
        escape = False
        
    raise ValueError("No balanced JSON structure found in response")


def extract_valid_json(text: str) -> str:
    """
    Extracts first valid JSON object or array from LLM response text.
    
    Args:
        text: Raw response text from LLM that should contain JSON
        
    Returns:
        str: Extracted JSON string ready for parsing
        
    Raises:
        ValueError: If no valid JSON structure found or parsing fails
        
    Example:
        >>> text = "Here's your schedule: {...schedule data...} Hope this helps!"
        >>> json_str = extract_valid_json(text)
        >>> data = json.loads(json_str)
        
    Educational Note:
        This robust extraction handles common LLM artifacts like markdown
        code fences (```json), explanatory preambles, and trailing commentary
        that would otherwise break simple json.loads() calls.
    """
    logger.debug(f"Extracting JSON from text (first 100 chars): {text[:100]}...")
    
    start, open_char, close_char = find_json_start(text)
    end = scan_for_balanced_close(text, start, open_char, close_char)
    
    extracted = text[start:end+1]
    logger.debug(f"Successfully extracted JSON (first 100 chars): {extracted[:100]}...")
    
    return extracted


def clean_json_text(text: str) -> str:
    """
    Removes common markdown code fence artifacts from LLM responses.
    
    Args:
        text: Raw LLM response potentially wrapped in code fences
        
    Returns:
        str: Cleaned text with code fences removed
        
    Educational Note:
        LLMs often wrap JSON in markdown code blocks (```json...```).
        Pre-cleaning simplifies downstream parsing and improves robustness.
    """
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = text.strip()
    return text
