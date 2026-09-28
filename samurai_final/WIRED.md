# SAMURAI WIRED — ComfyUI + A1111 Integration

## Quick Start

### A1111 (Automatic1111)
1. Launch webui with --api: `webui.bat --api --xformers`
2. Test: http://127.0.0.1:7860/sdapi/v1/options should return JSON
3. Run:
   python Code/samurai_cli.py run "ronin in neo-kyoto rain, cyberpunk" --backend a1111 --n 9

### ComfyUI
1. Launch: `python main.py --listen`
2. Test: http://127.0.0.1:8188/system_stats
3. Run:
   python Code/samurai_cli.py run "samurai armor, neon rim" --backend comfyui

### Mock (no server)
   python Code/samurai_cli.py run "test prompt" --backend mock

## Architecture

SamuraiGenerator (mock) -> queues 9 jobs with chaos sweep
WiredGenerator -> A1111Connector or ComfyUIConnector -> real images

A1111Connector:
 - txt2img with LoRA injection: <lora:name:weight>
 - batch() with seed 1000 + i*1337
 - saves a1111_{timestamp}.png

ComfyUIConnector:
 - queue_prompt() injects prompt into workflow JSON
 - Templates/workflows/samurai_base.json
 - Templates/workflows/samurai_lora_stack.json
 - Templates/workflows/samurai_upscale_facefix.json
 - wait_for_image() polls /history

## Workflows Included
- samurai_base.json — SDXL txt2img base
- samurai_lora_stack.json — samurai_armor 0.9 + neo_kyoto 0.7 stack
- samurai_upscale_facefix.json — 4x-UltraSharp upscale

## Config
Edit config.json to change URLs

## Windows Launcher
samurai.bat now supports:
samurai.bat run "prompt" --backend a1111
samurai.bat pipeline full --brief "ronin in rain"

## Smart Git Bypass

```powershell
# Initialize repo (one-time)
samurai.bat git init-smart

# Auto-sync: add + commit + push
samurai.bat git

# Manual commit with message
samurai.bat git commit-smart "added 10 soldier sequences"

# Push + push tags
samurai.bat git push-smart

# Tag release
samurai.bat git tag-smart v1.1.0-shadow
```

Behind the scenes: `git add.` + auto commit msg + manifest version bump + `git push -u origin main` + tag push.
