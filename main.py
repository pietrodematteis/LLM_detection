import sys
import json
from pathlib import Path
from engine.detector import detect_crypto_report
from parser.repo_parser import RepoParser
import time

DEFAULT_INPUT = "test/test_pyca_symmetric"
DEFAULT_OUTPUT = "artifacts/crypto_report.txt"
#DEFAULT_OUTPUT = "artifacts/crypto_report.json"
OLLAMA_BASE = "http://localhost:11434"
# MODEL = "qwen2.5:7b-instruct"
MODEL = "qwen2.5-coder:7b"
#MODEL = "qwen2.5-coder:3b"
temperature = 0
timeout = 180
num_ctx = 4096

def iter_py_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.rglob("*.py"))
    return [path]


def main():
    in_path = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT)
    out_file = Path(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT)

    py_files = iter_py_files(in_path)
    if not py_files:
        raise SystemExit(f"No .py files found under: {in_path}")

    all_reports: list[str] = []

    for f in py_files:
        report = detect_crypto_report(
            input_path=str(f),
            ollama_base=OLLAMA_BASE,
            model=MODEL,
            temperature=0,
            timeout=180,
            num_ctx=4096,   #4096
        )
        all_reports.append(report)
        clean = report.strip().replace("```json", "").replace("```", "").strip()
        #all_reports.extend(json.loads(clean))

    out_file.write_text("".join(all_reports), encoding="utf-8")
    print(f"Saved raw LLM reports to: {out_file}")
    # for debugging purpose
    # print("Saved LLM output to:", out_file)
    # with open(out_file, "w", encoding="utf-8") as f:
    #     json.dump(all_reports, f, indent=2)

if __name__ == "__main__":
    # main()
    start_time = time.time()
    repo_path = "/Users/adam/PycharmProjects/FBK /repo/flink"
    out_file = "parser_crypto.txt"
    repo_parser = RepoParser(repo_path, out_file, OLLAMA_BASE, MODEL, temperature, timeout, num_ctx)
    repo_parser.run()
    end_time = time.time()
    print("EXECUTION TIME: ", end_time - start_time)