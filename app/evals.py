from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .config import AppConfig
from .agentic import ask_question
from .cite import parse_labels_from_text


def load_questions(path: Path) -> List[Dict]:
    """
    questions.jsonl format:
    One JSON object per line:
    {"question": "...", "expected": "answer"|"refuse"}
    """
    items: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def run_eval(eval_path: str = "evalset/questions.jsonl", output_path: str = "data/eval_results.json") -> None:
    cfg = AppConfig()
    cfg.ensure_dirs()

    questions = load_questions(Path(eval_path))
    results = []

    for item in questions:
        q = item["question"]
        expected = item.get("expected", "answer")

        run = ask_question(cfg, question=q, debug=False, no_llm=False)
        ans = run.answer

        labels = parse_labels_from_text(ans.answer)
        has_citations = len(labels) > 0

        # Simple pass/fail checks
        refused_ok = (expected == "refuse" and ans.cannot_answer) or (expected != "refuse")
        citations_ok = has_citations or ans.cannot_answer  # if it refuses, citations not required

        results.append(
            {
                "question": q,
                "expected": expected,
                "cannot_answer": ans.cannot_answer,
                "confidence": ans.confidence,
                "has_citations": has_citations,
                "pass_refusal_rule": refused_ok,
                "pass_citation_rule": citations_ok,
            }
        )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Wrote eval results: {out}")
