"""
SAMURAI generator.py — Batch generation wrapper
Supports A1111 API, ComfyUI, and local diffusers
"""
import json, time, itertools
from pathlib import Path

class SamuraiGenerator:
    def __init__(self, model="SDXL", sampler="DPM++ 2M Karras", steps=30, cfg=7):
        self.model = model
        self.sampler = sampler
        self.steps = steps
        self.cfg = cfg
        self.queue = []

    def parse_prompt(self, raw):
        # Parse samurai chain syntax: /12-style cyberpunk + /34-keylight neon
        parts = [p.strip() for p in raw.split('+')]
        prompt_dict = {"subject":"", "style":[], "light":[], "camera":[], "fx":[]}
        for p in parts:
            if not p: continue
            if p.startswith('/'):
                prompt_dict["style"].append(p)
            else:
                prompt_dict["subject"] = p
        return prompt_dict

    def generate(self, prompt, n=9, chaos=0.3):
        """
        Generate n variations
        """
        parsed = self.parse_prompt(prompt)
        print(f"[generator] model={self.model} prompt={parsed}")
        jobs = []
        for i in range(n):
            seed = 1000 + i*1337
            job = {
                "id": f"sam_{int(time.time())}_{i}",
                "prompt": prompt,
                "parsed": parsed,
                "seed": seed,
                "chaos": chaos + (i*0.05),
                "sampler": self.sampler,
                "steps": self.steps,
                "cfg": self.cfg
            }
            jobs.append(job)
            print(f"  queued {job['id']} seed={seed} chaos={job['chaos']:.2f}")

        # Simulate generation (replace with real API call)
        # For real: requests.post("http://127.0.0.1:7860/sdapi/v1/txt2img", json=...)
        self.queue = jobs
        return jobs

    def save_manifest(self, path="manifest.json"):
        Path(path).write_text(json.dumps(self.queue, indent=2))
        print(f"[generator] manifest saved {path}")

if __name__ == "__main__":
    g = SamuraiGenerator()
    g.generate("ronin in neo-kyoto rain, /12-style cyberpunk + /34-keylight neon rim", n=9)
    g.save_manifest()
