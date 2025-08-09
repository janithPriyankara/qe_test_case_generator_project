"""Command-line interface for the test case generator."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from .config import Config
from .engine import MDTDTestEngine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    """Main application entry point."""

    parser = argparse.ArgumentParser(
        description="AI-Assisted MDTD Test Generator"
    )
    parser.add_argument("source", help="Source file or directory to analyze")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory (default: generated_<timestamp>)",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="html",
        choices=["html", "json", "python"],
        help="Output format",
    )
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = Config.load(args.config) if args.config else Config()
    engine = MDTDTestEngine(config)

    source_path = Path(args.source)
    if not source_path.exists():
        logger.error("Source path does not exist: %s", source_path)
        return 1

    result = await engine.analyze_and_generate_tests(source_path, args.format)

    if not result.get("success"):
        logger.error("Test generation failed: %s", result.get("error"))
        return 1

    output_dir = Path(args.output) if args.output else Path(
        f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    output_dir.mkdir(exist_ok=True)

    logger.info("Creating output directory: %s", output_dir)

    html_file = output_dir / "test_interface.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(result["web_interface"])

    analysis_file = output_dir / "source_analysis.json"
    analysis = result["analysis"]
    serializable_analysis = {}
    for key, value in analysis.items():
        if key == "functions":
            serializable_analysis[key] = [
                {
                    "name": f.name,
                    "parameters": f.parameters,
                    "return_type": f.return_type,
                    "docstring": f.docstring,
                    "complexity": f.complexity,
                    "line_number": f.line_number,
                    "language": f.language,
                    "visibility": f.visibility,
                    "is_static": f.is_static,
                    "has_state": f.has_state,
                    "error_conditions": f.error_conditions,
                }
                for f in value
            ]
        elif key == "classes":
            serializable_analysis[key] = [
                {
                    "name": c.name,
                    "methods": [m.name for m in c.methods],
                    "attributes": c.attributes,
                    "inheritance": c.inheritance,
                    "language": c.language,
                    "line_number": c.line_number,
                }
                for c in value
            ]
        else:
            serializable_analysis[key] = value

    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(serializable_analysis, f, indent=2, default=str)

    scenarios_file = output_dir / "test_scenarios.json"
    with open(scenarios_file, "w", encoding="utf-8") as f:
        json.dump(result.get("scenarios", []), f, indent=2, default=str)

    tests_file = output_dir / "generated_tests.json"
    with open(tests_file, "w", encoding="utf-8") as f:
        json.dump(result.get("tests", {}), f, indent=2, default=str)

    try:
        if result.get("report"):
            report_file = output_dir / "detailed_report.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(result["report"], f, indent=2, default=str)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not save detailed report: %s", exc)
        summary_file = output_dir / "summary_report.json"
        simple_report = {
            "timestamp": datetime.now().isoformat(),
            "source_file": str(source_path),
            "functions_analyzed": len(result["analysis"].get("functions", [])),
            "test_scenarios_generated": len(result.get("scenarios", [])),
            "files_generated": [
                html_file.name,
                analysis_file.name,
                scenarios_file.name,
                tests_file.name,
            ],
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(simple_report, f, indent=2, default=str)

    logger.info("Test generation completed successfully!")
    logger.info("Output directory: %s", output_dir)
    logger.info("HTML interface: %s", html_file)
    logger.info("Analysis results: %s", analysis_file)
    logger.info("Test scenarios: %s", scenarios_file)
    logger.info("Generated tests: %s", tests_file)

    return 0


def cli() -> int:
    """Console script entry point."""

    return asyncio.run(main())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())

