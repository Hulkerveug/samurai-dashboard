#!/usr/bin/env python3
"""
Hermes Mother Engine — Local FastAPI backend for Humanizer Lab
Run: uvicorn hermes_mother:app --host 127.0.0.1 --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Hermes Mother Engine", version="1.0")

class CompletionRequest(BaseModel):
    input_text: str  # Can contain blanks like "The primary defense against ___ injection is ___."
    context_type: str = "technical_completion"

classpletions_cache = {}  # Local cache for offline support

@app.post("/api/humanize-fill")
def humanize_and_fill(payload: CompletionRequest):
    """Fill blanks with humanized, natural language completions."""
    system_instruction = (
        "You are Hermes Agent, a local-first AI assistant. Your task is to intelligently and "
        "naturally fill in any blanks or incomplete text provided by the user. "
        "Ensure the tone is human, professional, concise, and avoids robotic AI phrasing. "
        "Use standard cybersecurity and software terminology."
    )
    
    prompt = f"{system_instruction}\n\nInput Text:\n{payload.input_text}\n\nCompleted & Humanized Version:"
    
    # Try local Ollama first
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "hermes3:8b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 200}
            },
            timeout=30
        )
        result = response.json().get("response", "")
        completions_cache[payload.input_text[:50]] = result
        return {"status": "success", "completion": result}
    except Exception as e:
        # Fallback: return deterministic completion
        return {
            "status": "fallback",
            "completion": _fallback_complete(payload.input_text, payload.context_type)
        }

def _fallback_complete(text: str, ctx: str) -> str:
    """Deterministic fallback when Ollama unavailable."""
    defaults = {
        "technical": "strict allowlist validation",
        "security": "least privilege policy",
        "creative": "a serene landscape at dusk",
        "code": "ALLOWED_URLS + SecurityError"
    }
    return text.replace("___", defaults.get(ctx, "proprietary solution"))

@app.get("/api/health")
def health_check():
    return {"status": "alive", "port": 8000}

@app.post("/api/reset-cache")
def reset_cache():
    completions_cache.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
    # Export for gunicorn: hermes_mother:app