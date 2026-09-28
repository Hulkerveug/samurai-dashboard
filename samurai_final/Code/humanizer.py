#!/usr/bin/env python3
"""
Humanizer Module — Fill-in-the-Blank completion with humanized tone
Integrated into Samurai for prompt engineering and security assessment
"""
import re
from datetime import datetime
from typing import List, Dict, Optional

# Pattern templates for different contexts
TEMPLATES = {
    "technical": {
        "patterns": [
            "The primary defense against ___ is ___",
            "To protect ___ from ___ exposure, use ___",
            "Input validation prevents ___ injection via ___",
            "The defense layer for ___ includes ___, ___, and ___",
            "Secure coding requires ___ before handling ___ data"
        ],
        "prefs": {
            "allowlist": "strict allowlist validation",
            "injection": "prompt injection attacks",
            "exposure": "environment variables",
            "protection": "input sanitization",
            "validation": "boundary checking"
        }
    },
    "security": {
        "patterns": [
            "Configure ___ role with ___ permissions",
            "Vulnerability CVE-___ requires patching ___ module",
            "Access control policy ___ defines ___ boundaries",
            "IAM user ___ must have ___ policy attached",
            "VPC subnet ___ routes traffic to ___ endpoint"
        ],
        "prefs": {
            "IAM": "least privilege IAM roles",
            "policy": "restrictive IAM policies",
            "VPC": "network segmentation",
            "endpoint": "private subnet endpoints",
            "permissions": "minimal required permissions"
        }
    },
    "creative": {
        "patterns": [
            "ronin in ___ field",
            "cyberpunk ___ at dusk",
            "melancholic ___ by the ___",
            "samurai warrior under ___ moon",
            "neo-kyoto district scene with ___ neon"
        ],
        "prefs": {
            "purple": "purple flower fields",
            "sunset": "golden sunset with volumetric haze",
            "neon": "neon rim lighting",
            "moon": "blood moon",
            "haze": "cinematic atmospheric haze"
        }
    },
    "code": {
        "patterns": [
            "def secure_connector(___):",
            "ALLOWED_URLS = ['___']",
            "def validate_input(___):",
            "class SecureClient(___):",
            "fetch_secure(___) throws SecurityError if ___"
        ],
        "prefs": {
            "url": "validated URL string",
            "input": "raw user input",
            "client": "requests.Session",
            "handler": "exception handler",
            "timeout": "5-second timeout"
        }
    }
}

# Historical completions for learning
COMPLETIONS_HISTORY = []

def normalize_text(text: str) -> str:
    """Strip artifacts, normalize whitespace."""
    text = re.sub(r'[\s_]+', ' ', text)  # normalize blanks
    text = re.sub(r'\s*[=:;,]\s*', r'\1 ', text)  # fix punctuation
    return text.strip()

def detect_blanks(text: str) -> List[int]:
    """Find positions of ___ in text."""
    return [m.start() for m in re.finditer(r'_{3,}', text)]

def count_blanks(text: str) -> int:
    """Count number of ___ occurrences."""
    return len(re.findall(r'_{3,}', text))

def categorize_context(text: str) -> str:
    """Detect context type from text patterns."""
    tech_keywords = ['def ', 'class ', 'return ', 'import ', 'api', 'endpoint', 'validation']
    security_keywords = ['IAM', 'VPC', 'policy', 'permission', 'vulnerability', 'CVE', 'role', 'subnet']
    creative_keywords = ['ronin', 'samurai', 'cyberpunk', 'neon', 'sunset', 'purple', 'field']
    code_keywords = ['ALLOWED', 'SecurityError', 'requests', 'timeout', 'validate']
    
    scores = {"technical": 0, "security": 0, "creative": 0, "code": 0}
    text_lower = text.lower()
    
    for kw in tech_keywords:
        if kw in text_lower: scores["technical"] += 1
    for kw in security_keywords:
        if kw in text_lower: scores["security"] += 1
    for kw in creative_keywords:
        if kw in text_lower: scores["creative"] += 1
    for kw in code_keywords:
        if kw in text_lower: scores["code"] += 1
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "technical"

def humanize(completion: str, style: str = "professional") -> str:
    """Apply humanized tone to completion."""
    # Add natural phrasing
    prefixes = ["Essentially,", "In practice,", "The core approach is to", "Fundamentally,"]
    suffixes = ["as per security best practices.", "following industry standards.", "to mitigate the risk."]
    
    if "allowlist" in completion.lower() and "whitelist" in completion.lower():
        completion = completion.replace("whitelist", "allowlist")
    
    if style == "creative":
        return completion[0].lower() + completion[1:]  # Lowercase start for creative
    
    return completion

def fill_blanks(text: str, context: str = "technical", force_fill: bool = True) -> Dict:
    """
    Main entry point for humanizer.
    Returns dict with filled text and metadata.
    """
    start_time = datetime.now()
    blanks = count_blanks(text)
    context_type = categorize_context(text) if context == "auto" else context
    
    # Generate completion
    if force_fill:
        # Use template-based completion for offline support
        template_entry = TEMPLATES.get(context_type, TEMPLATES["technical"])
        prefs = template_entry.get("prefs", {})
        
        # Simple fill: replace ___ with preferred terms
        completion = text
        blank_count = blanks
        for key, value in prefs.items():
            if blank_count <= 0: break
            completion = completion.replace("___", value, 1)
            blank_count -= 1
        
        # If still blanks, use generic
        while "___" in completion:
            completion = completion.replace("___", "a robust solution")
    else:
        completion = text
    
    # Post-process
    completion = humanize(completion, context_type)
    
    # Log history
    log_entry = {
        "input": text[:100],
        "output": completion[:100],
        "context": context_type,
        "blanks": blanks,
        "timestamp": start_time.isoformat()
    }
    COMPLETIONS_HISTORY.append(log_entry)
    if len(COMPLETIONS_HISTORY) > 100:
        COMPLETIONS_HISTORY = COMPLETIONS_HISTORY[-100:]
    
    return {
        "input": text,
        "output": completion,
        "blanks_filled": blanks,
        "context": context_type,
        "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000),
        "prefers": TEMPLATES.get(context_type, {}).get("prefs", {})
    }

def get_history(limit: int = 10) -> List[Dict]:
    """Get recent completion history."""
    return COMPLETIONS_HISTORY[-limit:]

# Integration for Samurai CLI
if __name__ == "__main__":
    import sys
    print("Humanizer Lab v1.0")
    print("Usage: python humanizer.py 'text with ___ blanks'")
    
    if len(sys.argv) > 1:
        result = fill_blanks(sys.argv[1])
        print(f"\nInput:  {result['input']}")
        print(f"Output: {result['output']}")
        print(f"Blanks filled: {result['blanks_filled']} in {result['latency_ms']}ms")