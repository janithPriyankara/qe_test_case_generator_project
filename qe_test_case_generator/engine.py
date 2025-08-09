"""Core engine orchestrating test generation workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from .config import Config
from .file_analyzer import FileAnalyzer
from .llm_controller import LLMController
from .report_generator import ReportGenerator
from .test_generator import TestGenerator
from .web_interface import WebInterface


logger = logging.getLogger(__name__)


class MDTDTestEngine:
    """Main Model-Driven Test Development engine."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.file_analyzer = FileAnalyzer(config)
        self.llm_controller = LLMController(config)
        self.test_generator = TestGenerator(config)
        self.web_interface = WebInterface(config)
        self.report_generator = ReportGenerator(config)

    async def analyze_and_generate_tests(
        self, source_path: Path, output_format: str = "html"
    ) -> Dict:
        """Analyze source files and generate tests."""

        try:
            logger.info("Starting analysis of: %s", source_path)

            analysis_result = await self.file_analyzer.analyze(source_path)
            logger.info(
                "Analysis completed. Found %s functions",
                len(analysis_result.get("functions", [])),
            )

            test_scenarios = await self.extract_test_scenarios(analysis_result)
            logger.info("Generated %s test scenarios", len(test_scenarios))

            generated_tests = await self.llm_controller.generate_comprehensive_tests(
                analysis_result, test_scenarios
            )
            logger.info("AI test generation completed")

            web_test_cases = await self.test_generator.create_web_test_cases(
                generated_tests, output_format
            )

            html_interface = await self.web_interface.create_test_interface(
                web_test_cases
            )

            report = await self.report_generator.generate_report(
                {
                    "source_analysis": analysis_result,
                    "test_scenarios": test_scenarios,
                    "generated_tests": generated_tests,
                    "web_interface": html_interface,
                }
            )

            return {
                "analysis": analysis_result,
                "scenarios": test_scenarios,
                "tests": generated_tests,
                "web_interface": html_interface,
                "report": report,
                "success": True,
            }

        except Exception as exc:  # noqa: BLE001
            logger.error("Error in test generation: %s", exc)
            return {"error": str(exc), "success": False}

    async def extract_test_scenarios(self, analysis_result: Dict) -> List[Dict]:
        """Extract test scenarios based on MDTD principles."""

        scenarios: List[Dict] = []

        for function in analysis_result.get("functions", []):
            scenarios.extend(self._create_equivalence_partition_tests(function))
            scenarios.extend(self._create_boundary_value_tests(function))
            scenarios.extend(self._create_error_condition_tests(function))
            if function.has_state:
                scenarios.extend(self._create_state_transition_tests(function))

        return scenarios

    def _create_equivalence_partition_tests(self, function) -> List[Dict]:
        """Create tests based on equivalence partitioning."""

        tests = []
        for param in function.parameters:
            param_type = param.get("type", "unknown")

            if param_type in ["int", "float", "number"]:
                tests.extend(
                    [
                        {
                            "type": "equivalence_partition",
                            "category": "positive_numbers",
                            "function": function.name,
                            "parameter": param["name"],
                            "test_values": [1, 10, 100, 1.5, 3.14],
                            "expected_behavior": "normal_operation",
                        },
                        {
                            "type": "equivalence_partition",
                            "category": "negative_numbers",
                            "function": function.name,
                            "parameter": param["name"],
                            "test_values": [-1, -10, -100, -1.5, -3.14],
                            "expected_behavior": "normal_operation",
                        },
                        {
                            "type": "equivalence_partition",
                            "category": "zero",
                            "function": function.name,
                            "parameter": param["name"],
                            "test_values": [0, 0.0],
                            "expected_behavior": "edge_case",
                        },
                    ]
                )

            elif param_type in ["string", "str"]:
                tests.extend(
                    [
                        {
                            "type": "equivalence_partition",
                            "category": "valid_strings",
                            "function": function.name,
                            "parameter": param["name"],
                            "test_values": ["hello", "test123", "valid_input"],
                            "expected_behavior": "normal_operation",
                        },
                        {
                            "type": "equivalence_partition",
                            "category": "empty_strings",
                            "function": function.name,
                            "parameter": param["name"],
                            "test_values": ["", "   ", None],
                            "expected_behavior": "edge_case",
                        },
                    ]
                )

        return tests

    def _create_boundary_value_tests(self, function) -> List[Dict]:
        """Create boundary value analysis tests."""

        tests = []
        for param in function.parameters:
            param_type = param.get("type", "unknown")

            if param_type in ["int", "float", "number"]:
                tests.append(
                    {
                        "type": "boundary_value",
                        "category": "numeric_boundaries",
                        "function": function.name,
                        "parameter": param["name"],
                        "test_values": [
                            float("-inf"),
                            -1000000,
                            -1,
                            0,
                            1,
                            1000000,
                            float("inf"),
                        ],
                        "expected_behavior": "boundary_testing",
                    }
                )

        return tests

    def _create_error_condition_tests(self, function) -> List[Dict]:
        """Create error condition tests."""

        return [
            {
                "type": "error_condition",
                "category": "type_errors",
                "function": function.name,
                "test_values": [None, [], {}, "invalid_type"],
                "expected_behavior": "error_handling",
            }
        ]

    def _create_state_transition_tests(self, function) -> List[Dict]:
        """Create state transition tests for stateful functions."""

        return [
            {
                "type": "state_transition",
                "category": "state_changes",
                "function": function.name,
                "test_sequence": ["init", "action1", "action2", "verify"],
                "expected_behavior": "state_verification",
            }
        ]

