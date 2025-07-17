import os
import argparse
from dbt_ai.dbt import DbtModelProcessor
from dbt_ai.report import generate_html_report


def main():
    parser = argparse.ArgumentParser(description="Run AI-powered dbt model review.")
    parser.add_argument("project_path", help="Path to the dbt project directory")
    parser.add_argument("--level", choices=["basic", "advanced"], default="basic", help="Review level")
    parser.add_argument("--provider", default="openai", help="LLM provider (default: openai)")
    parser.add_argument("--model", default="gpt-4", help="LLM model name (default: gpt-4)")
    parser.add_argument("--output", default="dbt_ai_report.html", help="Path to save the HTML report")

    args = parser.parse_args()

    processor = DbtModelProcessor(dbt_project_path=args.project_path)
    models, missing_metadata = processor.process_dbt_models(level=args.level)

    print(f"✅ Reviewed {len(models)} models. Generating report...")
    generate_html_report(models, args.output, missing_metadata)
    print(f"📄 Report saved to {args.output}")


if __name__ == "__main__":
    main()
