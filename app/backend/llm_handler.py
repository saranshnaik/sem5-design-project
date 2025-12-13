from datetime import datetime
from utils import compare_responses


def query_llm(prompt: str) -> str:
    """Mock LLM response placeholder."""
    return f"[Simulated LLM Response] {prompt}"


def log_quality(original, filtered, orig_resp, filt_resp):
    with open("quality_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now()} ===\n")
        f.write(f"Original: {original}\nFiltered: {filtered}\n")
        f.write(f"Orig Resp: {orig_resp}\nFilt Resp: {filt_resp}\n")
        f.write(f"Similarity Score: {compare_responses(orig_resp, filt_resp)}\n")
