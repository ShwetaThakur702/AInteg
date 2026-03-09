"""
test_pipeline.py
================
CLI tool to test the API Integration pipeline without opening the browser.

Usage:
    python3 test_pipeline.py <spec_file_or_url>

Examples:
    python3 test_pipeline.py petstore.yaml
    python3 test_pipeline.py stripe.json
    python3 test_pipeline.py https://petstore3.swagger.io/api/v3/openapi.json

Output files are saved to: output/<job_id>/
"""

import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error

API_BASE = "http://localhost:8000"


# ── Colour helpers (terminal output) ─────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GREY   = "\033[90m"


def green(s):  return f"{GREEN}{s}{RESET}"
def blue(s):   return f"{BLUE}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def red(s):    return f"{RED}{s}{RESET}"
def grey(s):   return f"{GREY}{s}{RESET}"
def bold(s):   return f"{BOLD}{s}{RESET}"


# ── Step 1: Submit the spec ───────────────────────────────────

def submit_spec(input_arg: str) -> str:
    """POST /api/run-pipeline with a file or URL. Returns job_id."""
    is_url = input_arg.startswith("http://") or input_arg.startswith("https://")

    if is_url:
        print(f"  {blue('→')} Submitting URL: {input_arg}")
        # Send as form field
        data = urllib.parse.urlencode({"url": input_arg}).encode()
        req = urllib.request.Request(
            f"{API_BASE}/api/run-pipeline",
            data=data,
            method="POST",
        )
    else:
        print(f"  {blue('→')} Submitting file: {input_arg}")
        # Read file and send as multipart
        with open(input_arg, "rb") as f:
            file_bytes = f.read()

        filename = input_arg.split("/")[-1]
        boundary = b"----TestPipelineBoundary"
        body = (
            b"--" + boundary + b"\r\n"
            b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n'
            b"Content-Type: application/octet-stream\r\n\r\n"
            + file_bytes
            + b"\r\n--" + boundary + b"--\r\n"
        )
        req = urllib.request.Request(
            f"{API_BASE}/api/run-pipeline",
            data=body,
            method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary.decode()}"},
        )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result["job_id"]
    except urllib.error.URLError as e:
        print(red(f"\n  ✗ Could not reach backend at {API_BASE}"))
        print(grey(f"    Is the server running?  uvicorn main:app --reload --port 8000"))
        sys.exit(1)


# ── Step 2: Poll for status ───────────────────────────────────

STAGE_LABELS = {
    "chain_1":    "Chain 1 · Spec Analysis  ",
    "chain_2":    "Chain 2 · Client Stubs   ",
    "chain_3":    "Chain 3 · Usage Examples ",
    "chain_4":    "Chain 4 · Contract Tests ",
    "validation": "Validation · AST + pytest",
}

def poll_status(job_id: str) -> dict:
    """Poll /api/pipeline-status/{job_id} until complete or error."""
    url = f"{API_BASE}/api/pipeline-status/{job_id}"
    last_stage = None

    print()
    while True:
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                for raw_line in resp:
                    line = raw_line.decode().strip()
                    if not line.startswith("data:"):
                        continue
                    state = json.loads(line[5:].strip())

                    stage   = state.get("stage")
                    status  = state.get("status")
                    progress = state.get("progress", 0)

                    if stage and stage != last_stage:
                        label = STAGE_LABELS.get(stage, stage)
                        print(f"  {yellow('⟳')} {label}  {grey(str(progress) + '%')}")
                        last_stage = stage

                    if status == "complete":
                        print(f"  {green('✓')} Complete  {grey('100%')}")
                        return state

                    if status == "error":
                        return state

        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
            continue


# ── Step 3: Download output files ────────────────────────────

def download_files(job_id: str, output_files: list[str]) -> str:
    """Download all generated .py files into output/<job_id>/."""
    import os
    out_dir = f"output/{job_id}"
    os.makedirs(out_dir, exist_ok=True)

    print()
    for filename in output_files:
        url = f"{API_BASE}/api/results/{job_id}/{filename}"
        dest = f"{out_dir}/{filename}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read()
        with open(dest, "wb") as f:
            f.write(content)
        size_kb = len(content) / 1024
        print(f"  {green('↓')} {bold(filename):<28}  {grey(f'{size_kb:.1f} KB → {dest}')}")

    return out_dir


# ── Main ──────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f"\n{bold('Usage:')}  python3 test_pipeline.py <spec_file_or_url>\n")
        print("Examples:")
        print("  python3 test_pipeline.py petstore.yaml")
        print("  python3 test_pipeline.py https://petstore3.swagger.io/api/v3/openapi.json\n")
        sys.exit(1)

    input_arg = sys.argv[1]

    print(f"\n{bold('API Integration Agent — Test Runner')}")
    print("─" * 44)

    # 1. Submit
    print(f"\n{bold('[1/3] Submitting spec')}")
    job_id = submit_spec(input_arg)
    print(f"  {green('✓')} Job created: {grey(job_id)}")

    # 2. Poll
    print(f"\n{bold('[2/3] Running pipeline')}")
    state = poll_status(job_id)

    if state.get("status") == "error":
        print(f"\n  {red('✗ Pipeline failed:')}")
        print(f"  {grey(state.get('error', 'Unknown error'))}")
        sys.exit(1)

    # 3. Download
    output_files = state.get("output_files", [])
    print(f"\n{bold('[3/3] Downloading files')}")
    out_dir = download_files(job_id, output_files)

    # Summary
    summary = state.get("spec_summary")
    print(f"\n{'─' * 44}")
    print(f"{green(bold('Done!'))}  Files saved to {bold(out_dir)}/\n")

    if summary:
        endpoints = summary.get("endpoints", [])
        print(f"  {grey('Base URL:')}    {summary.get('base_url', '—')}")
        print(f"  {grey('Auth:')}        {summary.get('auth_type', '—')}")
        print(f"  {grey('Endpoints:')}   {len(endpoints)}")
        print()


if __name__ == "__main__":
    main()
