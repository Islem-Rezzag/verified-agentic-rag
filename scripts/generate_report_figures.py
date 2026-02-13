from __future__ import annotations

import argparse

from verified_agentic_rag.report_figures import generate_result_figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate showcase figures from evaluation CSV.")
    parser.add_argument(
        "--csv-path",
        default="data/reports/full_system_eval_question_results_20260212.csv",
        help="Question-level CSV input path",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/figures",
        help="Output directory for generated PNG figures",
    )
    args = parser.parse_args()

    outputs = generate_result_figures(csv_path=args.csv_path, output_dir=args.output_dir)
    for path in outputs:
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()
