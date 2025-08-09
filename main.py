#!/usr/bin/env python3
"""
AI-Assisted Model Driven Test Engineering Prototype
Main application entry point for multi-language source analysis and test generation
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.file_analyzer import FileAnalyzer
from src.llm_controller import LLMController
from src.test_generator import TestGenerator
from src.web_interface import WebInterface
from src.report_generator import ReportGenerator
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MDTDTestEngine:
    """
    Main Model-Driven Test Development Engine
    Orchestrates the entire process from source analysis to test generation
    """

    def __init__(self, config: Config):
        self.config = config
        self.file_analyzer = FileAnalyzer(config)
        self.llm_controller = LLMController(config)
        self.test_generator = TestGenerator(config)
        self.web_interface = WebInterface(config)
        self.report_generator = ReportGenerator(config)

    async def analyze_and_generate_tests(
        self,
        source_path: Path,
        output_format: str = "html"
    ) -> Dict:
        """
        Main workflow: Analyze source files and generate comprehensive tests

        Args:
            source_path: Path to source file or directory
            output_format: Output format (html, json, python, etc.)

        Returns:
            Dict containing analysis results and generated tests
        """
        try:
            logger.info(f"🔍 Starting analysis of: {source_path}")

            # Step 1: Analyze source files
            analysis_result = await self.file_analyzer.analyze(source_path)
            logger.info(f"✅ Analysis completed. Found {len(analysis_result.get('functions', []))} functions")

            # Step 2: Extract test scenarios using MDTD principles
            test_scenarios = await self.extract_test_scenarios(analysis_result)
            logger.info(f"📋 Generated {len(test_scenarios)} test scenarios")

            # Step 3: Generate tests using LLM
            generated_tests = await self.llm_controller.generate_comprehensive_tests(
                analysis_result, test_scenarios
            )
            logger.info("🤖 AI test generation completed")

            # Step 4: Create test cases for web interface
            web_test_cases = await self.test_generator.create_web_test_cases(
                generated_tests, output_format
            )

            # Step 5: Generate HTML interface
            html_interface = await self.web_interface.create_test_interface(web_test_cases)

            # Step 6: Generate comprehensive report
            report = await self.report_generator.generate_report({
                'source_analysis': analysis_result,
                'test_scenarios': test_scenarios,
                'generated_tests': generated_tests,
                'web_interface': html_interface
            })

            return {
                'analysis': analysis_result,
                'scenarios': test_scenarios,
                'tests': generated_tests,
                'web_interface': html_interface,
                'report': report,
                'success': True
            }

        except Exception as e:
            logger.error(f"❌ Error in test generation: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }

    async def extract_test_scenarios(self, analysis_result: Dict) -> List[Dict]:
        """
        Extract test scenarios based on MDTD principles

        Args:
            analysis_result: Results from source code analysis

        Returns:
            List of test scenarios following MDTD methodology
        """
        scenarios = []

        for function in analysis_result.get('functions', []):
            # Equivalence partitioning
            scenarios.extend(self._create_equivalence_partition_tests(function))

            # Boundary value analysis
            scenarios.extend(self._create_boundary_value_tests(function))

            # Error condition testing
            scenarios.extend(self._create_error_condition_tests(function))

            # State transition testing (if applicable)
            if function.has_state:
                scenarios.extend(self._create_state_transition_tests(function))

        return scenarios

    def _create_equivalence_partition_tests(self, function) -> List[Dict]:
        """Create tests based on equivalence partitioning"""
        tests = []

        for param in function.parameters:
            param_type = param.get('type', 'unknown')

            if param_type in ['int', 'float', 'number']:
                tests.extend([
                    {
                        'type': 'equivalence_partition',
                        'category': 'positive_numbers',
                        'function': function.name,
                        'parameter': param['name'],
                        'test_values': [1, 10, 100, 1.5, 3.14],
                        'expected_behavior': 'normal_operation'
                    },
                    {
                        'type': 'equivalence_partition',
                        'category': 'negative_numbers',
                        'function': function.name,
                        'parameter': param['name'],
                        'test_values': [-1, -10, -100, -1.5, -3.14],
                        'expected_behavior': 'normal_operation'
                    },
                    {
                        'type': 'equivalence_partition',
                        'category': 'zero',
                        'function': function.name,
                        'parameter': param['name'],
                        'test_values': [0, 0.0],
                        'expected_behavior': 'edge_case'
                    }
                ])

            elif param_type in ['string', 'str']:
                tests.extend([
                    {
                        'type': 'equivalence_partition',
                        'category': 'valid_strings',
                        'function': function.name,
                        'parameter': param['name'],
                        'test_values': ['hello', 'test123', 'valid_input'],
                        'expected_behavior': 'normal_operation'
                    },
                    {
                        'type': 'equivalence_partition',
                        'category': 'empty_strings',
                        'function': function.name,
                        'parameter': param['name'],
                        'test_values': ['', '   ', None],
                        'expected_behavior': 'edge_case'
                    }
                ])

        return tests

    def _create_boundary_value_tests(self, function) -> List[Dict]:
        """Create boundary value analysis tests"""
        tests = []

        for param in function.parameters:
            param_type = param.get('type', 'unknown')

            if param_type in ['int', 'float', 'number']:
                tests.append({
                    'type': 'boundary_value',
                    'category': 'numeric_boundaries',
                    'function': function.name,
                    'parameter': param['name'],
                    'test_values': [
                        float('-inf'), -1000000, -1, 0, 1, 1000000, float('inf')
                    ],
                    'expected_behavior': 'boundary_testing'
                })

        return tests

    def _create_error_condition_tests(self, function) -> List[Dict]:
        """Create error condition tests"""
        tests = []

        # Type error tests
        tests.append({
            'type': 'error_condition',
            'category': 'type_errors',
            'function': function.name,
            'test_values': [None, [], {}, 'invalid_type'],
            'expected_behavior': 'error_handling'
        })

        return tests

    def _create_state_transition_tests(self, function) -> List[Dict]:
        """Create state transition tests for stateful functions"""
        tests = []

        # This would be expanded based on state analysis
        tests.append({
            'type': 'state_transition',
            'category': 'state_changes',
            'function': function.name,
            'test_sequence': ['init', 'action1', 'action2', 'verify'],
            'expected_behavior': 'state_verification'
        })

        return tests


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='AI-Assisted MDTD Test Generator')
    parser.add_argument('source', help='Source file or directory to analyze')
    parser.add_argument('--output', '-o', default=None, help='Output directory (default: generated_<timestamp>)')
    parser.add_argument('--format', '-f', default='html', choices=['html', 'json', 'python'],
                       help='Output format')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = Config.load(args.config) if args.config else Config()

    # Initialize test engine
    engine = MDTDTestEngine(config)

    # Run analysis and generation
    source_path = Path(args.source)
    if not source_path.exists():
        logger.error(f"Source path does not exist: {source_path}")
        return 1

    result = await engine.analyze_and_generate_tests(source_path, args.format)

    if result['success']:
        # Create timestamped output directory if not specified
        if args.output:
            output_dir = Path(args.output)
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"generated_{timestamp}")

        output_dir.mkdir(exist_ok=True)

        logger.info(f"📁 Creating output directory: {output_dir}")

        # Save HTML interface
        html_file = output_dir / 'test_interface.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(result['web_interface'])

        # Save analysis results
        analysis_file = output_dir / 'source_analysis.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            # Convert dataclass objects to dict for JSON serialization
            analysis = result['analysis']
            serializable_analysis = {}
            for key, value in analysis.items():
                if key == 'functions':
                    serializable_analysis[key] = [
                        {
                            'name': f.name,
                            'parameters': f.parameters,
                            'return_type': f.return_type,
                            'docstring': f.docstring,
                            'complexity': f.complexity,
                            'line_number': f.line_number,
                            'language': f.language,
                            'visibility': f.visibility,
                            'is_static': f.is_static,
                            'has_state': f.has_state,
                            'error_conditions': f.error_conditions
                        } for f in value
                    ]
                elif key == 'classes':
                    serializable_analysis[key] = [
                        {
                            'name': c.name,
                            'methods': [m.name for m in c.methods],
                            'attributes': c.attributes,
                            'inheritance': c.inheritance,
                            'language': c.language,
                            'line_number': c.line_number
                        } for c in value
                    ]
                else:
                    serializable_analysis[key] = value

            json.dump(serializable_analysis, f, indent=2, default=str)

        # Save test scenarios
        scenarios_file = output_dir / 'test_scenarios.json'
        with open(scenarios_file, 'w', encoding='utf-8') as f:
            json.dump(result.get('scenarios', []), f, indent=2, default=str)

        # Save generated tests
        tests_file = output_dir / 'generated_tests.json'
        with open(tests_file, 'w', encoding='utf-8') as f:
            json.dump(result.get('tests', {}), f, indent=2, default=str)

        # Save report (with error handling)
        try:
            if result.get('report'):
                report_file = output_dir / 'detailed_report.json'
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(result['report'], f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save detailed report: {str(e)}")
            # Create simple summary instead
            summary_file = output_dir / 'summary_report.json'
            simple_report = {
                'timestamp': datetime.now().isoformat(),
                'source_file': str(source_path),
                'functions_analyzed': len(result['analysis'].get('functions', [])),
                'test_scenarios_generated': len(result.get('scenarios', [])),
                'files_generated': [
                    html_file.name,
                    analysis_file.name,
                    scenarios_file.name,
                    tests_file.name
                ]
            }
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(simple_report, f, indent=2, default=str)

        logger.info(f"✅ Test generation completed successfully!")
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info(f"🌐 HTML interface: {html_file}")
        logger.info(f"📊 Analysis results: {analysis_file}")
        logger.info(f"🧪 Test scenarios: {scenarios_file}")
        logger.info(f"🤖 Generated tests: {tests_file}")

        return 0
    else:
        logger.error(f"❌ Test generation failed: {result['error']}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
