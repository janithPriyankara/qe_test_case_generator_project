"""
Report Generator for MDTD Test Engine
Creates comprehensive reports from test execution results
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from .config import Config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive reports from test results"""

    def __init__(self, config: Config):
        self.config = config

    async def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive test report

        Args:
            data: Combined data from all analysis and test execution phases

        Returns:
            Comprehensive report dictionary
        """
        try:
            logger.info("Generating comprehensive test report...")

            report = {
                'metadata': self._generate_metadata(),
                'executive_summary': self._generate_executive_summary(data),
                'source_analysis': self._analyze_source_code(data.get('source_analysis', {})),
                'test_coverage': self._analyze_test_coverage(data),
                'test_execution': self._analyze_test_execution(data),
                'quality_metrics': self._calculate_quality_metrics(data),
                'recommendations': self._generate_recommendations(data),
                'appendices': self._generate_appendices(data)
            }

            logger.info("Report generation completed")
            return report

        except Exception as e:
            logger.error("Error generating report: {}".format(str(e)))
            raise

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'generated_at': datetime.now().isoformat(),
            'generator_version': '1.0.0',
            'report_type': 'MDTD Test Analysis Report',
            'format_version': '2023.1'
        }

    def _generate_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        source_analysis = data.get('source_analysis', {})
        generated_tests = data.get('generated_tests', {})

        functions_analyzed = len(source_analysis.get('functions', []))
        test_suites_generated = len(generated_tests.get('function_tests', []))
        languages_detected = len(source_analysis.get('language_distribution', {}))

        complexity_metrics = source_analysis.get('complexity_metrics', {})
        avg_complexity = complexity_metrics.get('average_complexity', 0)

        return {
            'overview': {
                'functions_analyzed': functions_analyzed,
                'test_suites_generated': test_suites_generated,
                'languages_detected': languages_detected,
                'average_complexity': round(avg_complexity, 2)
            },
            'key_findings': [
                f"Analyzed {functions_analyzed} functions across {languages_detected} programming languages",
                f"Generated {test_suites_generated} comprehensive test suites using MDTD principles",
                f"Average cyclomatic complexity: {round(avg_complexity, 2)}",
                f"Test coverage includes: equivalence partitioning, boundary value analysis, error conditions"
            ],
            'quality_assessment': self._assess_overall_quality(data),
            'risk_assessment': self._assess_risks(data)
        }

    def _analyze_source_code(self, source_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze source code quality and characteristics"""
        functions = source_analysis.get('functions', [])
        classes = source_analysis.get('classes', [])
        complexity_metrics = source_analysis.get('complexity_metrics', {})

        # Language distribution
        language_dist = source_analysis.get('language_distribution', {})

        # Function analysis
        function_analysis = {
            'total_functions': len(functions),
            'complexity_distribution': self._analyze_complexity_distribution(functions),
            'parameter_analysis': self._analyze_parameters(functions),
            'return_type_analysis': self._analyze_return_types(functions),
            'error_handling_analysis': self._analyze_error_handling(functions)
        }

        # Class analysis
        class_analysis = {
            'total_classes': len(classes),
            'inheritance_analysis': self._analyze_inheritance(classes),
            'method_distribution': self._analyze_method_distribution(classes)
        }

        return {
            'language_distribution': language_dist,
            'function_analysis': function_analysis,
            'class_analysis': class_analysis,
            'complexity_metrics': complexity_metrics,
            'code_quality_indicators': self._calculate_code_quality_indicators(source_analysis)
        }

    def _analyze_test_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage across different dimensions"""
        generated_tests = data.get('generated_tests', {})
        test_scenarios = data.get('test_scenarios', [])

        # Coverage by category
        category_coverage = {}
        for scenario in test_scenarios:
            category = scenario.get('category', 'unknown')
            category_coverage[category] = category_coverage.get(category, 0) + 1

        # Coverage by function
        function_tests = generated_tests.get('function_tests', [])
        function_coverage = {}
        for func_test in function_tests:
            func_name = func_test.get('function', 'unknown')
            scenarios = func_test.get('scenarios', [])
            function_coverage[func_name] = len(scenarios)

        # Test type coverage
        test_types = {
            'unit_tests': len(function_tests),
            'integration_tests': len(generated_tests.get('integration_tests', [])),
            'performance_tests': len(generated_tests.get('performance_tests', [])),
            'security_tests': len(generated_tests.get('security_tests', []))
        }

        return {
            'category_coverage': category_coverage,
            'function_coverage': function_coverage,
            'test_type_coverage': test_types,
            'coverage_summary': {
                'total_test_scenarios': len(test_scenarios),
                'functions_with_tests': len([f for f in function_coverage.values() if f > 0]),
                'average_tests_per_function': round(sum(function_coverage.values()) / max(len(function_coverage), 1), 2)
            }
        }

    def _analyze_test_execution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test execution results if available"""
        # This would be populated with actual execution results
        # For now, we'll provide a structure for when execution results are available

        return {
            'execution_summary': {
                'total_tests_executed': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'execution_time_total': 0,
                'average_execution_time': 0
            },
            'test_results_by_category': {},
            'performance_metrics': {
                'fastest_test': None,
                'slowest_test': None,
                'memory_usage': None
            },
            'failure_analysis': {
                'common_failure_patterns': [],
                'error_types': {},
                'failure_rate_by_category': {}
            }
        }

    def _calculate_quality_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various quality metrics"""
        source_analysis = data.get('source_analysis', {})
        functions = source_analysis.get('functions', [])

        if not functions:
            return {}

        # Complexity metrics
        complexities = [f.complexity for f in functions]

        # Documentation metrics
        documented_functions = len([f for f in functions if f.docstring])
        documentation_coverage = documented_functions / len(functions) * 100

        # Error handling metrics
        functions_with_error_handling = len([f for f in functions if f.error_conditions])
        error_handling_coverage = functions_with_error_handling / len(functions) * 100

        # Testability metrics
        test_opportunities = source_analysis.get('test_opportunities', [])
        testability_score = self._calculate_testability_score(functions, test_opportunities)

        return {
            'complexity_metrics': {
                'average_complexity': round(sum(complexities) / len(complexities), 2),
                'max_complexity': max(complexities),
                'min_complexity': min(complexities),
                'high_complexity_functions': [f.name for f in functions if f.complexity > 10]
            },
            'documentation_metrics': {
                'documentation_coverage': round(documentation_coverage, 2),
                'documented_functions': documented_functions,
                'total_functions': len(functions)
            },
            'error_handling_metrics': {
                'error_handling_coverage': round(error_handling_coverage, 2),
                'functions_with_error_handling': functions_with_error_handling
            },
            'testability_metrics': {
                'testability_score': testability_score,
                'test_opportunities_identified': len(test_opportunities)
            }
        }

    def _generate_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []

        source_analysis = data.get('source_analysis', {})
        complexity_metrics = source_analysis.get('complexity_metrics', {})
        functions = source_analysis.get('functions', [])

        # Complexity recommendations
        high_complexity_funcs = complexity_metrics.get('high_complexity_functions', [])
        if len(high_complexity_funcs) > 0:
            recommendations.append({
                'category': 'Code Complexity',
                'priority': 'High',
                'title': 'Reduce Cyclomatic Complexity',
                'description': f'Found {len(high_complexity_funcs)} functions with high cyclomatic complexity (>10)',
                'action_items': [
                    'Refactor complex functions into smaller, more manageable units',
                    'Extract common logic into separate helper functions',
                    'Consider using design patterns to reduce complexity'
                ],
                'affected_functions': high_complexity_funcs
            })

        # Documentation recommendations
        undocumented_functions = [f for f in functions if not f.docstring]
        if len(undocumented_functions) > len(functions) * 0.3:  # More than 30% undocumented
            recommendations.append({
                'category': 'Documentation',
                'priority': 'Medium',
                'title': 'Improve Code Documentation',
                'description': f'{len(undocumented_functions)} functions lack documentation',
                'action_items': [
                    'Add docstrings to all public functions',
                    'Document complex algorithms and business logic',
                    'Include parameter and return value descriptions'
                ],
                'affected_functions': [f.name for f in undocumented_functions[:10]]  # Show first 10
            })

        # Error handling recommendations
        functions_without_error_handling = [f for f in functions if not f.error_conditions]
        if len(functions_without_error_handling) > len(functions) * 0.5:  # More than 50% without error handling
            recommendations.append({
                'category': 'Error Handling',
                'priority': 'High',
                'title': 'Implement Comprehensive Error Handling',
                'description': f'{len(functions_without_error_handling)} functions lack proper error handling',
                'action_items': [
                    'Add try-catch blocks for potential failure points',
                    'Validate input parameters',
                    'Provide meaningful error messages',
                    'Log errors appropriately'
                ],
                'affected_functions': [f.name for f in functions_without_error_handling[:10]]
            })

        # Testing recommendations
        generated_tests = data.get('generated_tests', {})
        test_coverage = self._analyze_test_coverage(data)

        if test_coverage.get('coverage_summary', {}).get('average_tests_per_function', 0) < 3:
            recommendations.append({
                'category': 'Test Coverage',
                'priority': 'Medium',
                'title': 'Increase Test Coverage',
                'description': 'Functions have insufficient test coverage',
                'action_items': [
                    'Implement the generated test cases',
                    'Add edge case testing',
                    'Include negative test scenarios',
                    'Set up automated test execution'
                ]
            })

        return recommendations

    def _generate_appendices(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appendices with detailed data"""
        return {
            'function_details': self._create_function_details_appendix(data),
            'test_scenarios_details': self._create_test_scenarios_appendix(data),
            'generated_code_samples': self._create_code_samples_appendix(data),
            'configuration_details': self._create_configuration_appendix()
        }

    # Helper methods for detailed analysis
    def _analyze_complexity_distribution(self, functions: List) -> Dict[str, int]:
        """Analyze distribution of cyclomatic complexity"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}

        for func in functions:
            complexity = func.complexity
            if complexity <= 3:
                distribution['low'] += 1
            elif complexity <= 7:
                distribution['medium'] += 1
            elif complexity <= 10:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1

        return distribution

    def _analyze_parameters(self, functions: List) -> Dict[str, Any]:
        """Analyze function parameters"""
        if not functions:
            return {
                'average_parameters': 0,
                'max_parameters': 0,
                'functions_with_many_params': 0
            }

        param_counts = [len(f.parameters) for f in functions]

        return {
            'average_parameters': round(sum(param_counts) / max(len(param_counts), 1), 2),
            'max_parameters': max(param_counts) if param_counts else 0,
            'functions_with_many_params': len([c for c in param_counts if c > 5])
        }

    def _analyze_return_types(self, functions: List) -> Dict[str, int]:
        """Analyze return types distribution"""
        return_types = {}
        for func in functions:
            ret_type = func.return_type or 'unknown'
            return_types[ret_type] = return_types.get(ret_type, 0) + 1
        return return_types

    def _analyze_error_handling(self, functions: List) -> Dict[str, Any]:
        """Analyze error handling patterns"""
        error_types = {}
        for func in functions:
            for error in func.error_conditions:
                error_types[error] = error_types.get(error, 0) + 1

        return {
            'common_error_types': error_types,
            'functions_with_error_handling': len([f for f in functions if f.error_conditions])
        }

    def _analyze_inheritance(self, classes: List) -> Dict[str, Any]:
        """Analyze class inheritance patterns"""
        inheritance_depths = [len(cls.inheritance) for cls in classes]

        return {
            'average_inheritance_depth': round(sum(inheritance_depths) / max(len(inheritance_depths), 1), 2),
            'max_inheritance_depth': max(inheritance_depths) if inheritance_depths else 0,
            'classes_with_inheritance': len([d for d in inheritance_depths if d > 0])
        }

    def _analyze_method_distribution(self, classes: List) -> Dict[str, Any]:
        """Analyze method distribution in classes"""
        method_counts = [len(cls.methods) for cls in classes]

        return {
            'average_methods_per_class': round(sum(method_counts) / max(len(method_counts), 1), 2),
            'max_methods_in_class': max(method_counts) if method_counts else 0,
            'classes_with_many_methods': len([c for c in method_counts if c > 10])
        }

    def _calculate_code_quality_indicators(self, source_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall code quality indicators"""
        functions = source_analysis.get('functions', [])
        complexity_metrics = source_analysis.get('complexity_metrics', {})

        if not functions:
            return {}

        # Calculate quality score (0-100)
        avg_complexity = complexity_metrics.get('average_complexity', 0)
        complexity_score = max(0, 100 - (avg_complexity * 5))  # Penalty for high complexity

        documented_ratio = len([f for f in functions if f.docstring]) / len(functions)
        documentation_score = documented_ratio * 100

        error_handling_ratio = len([f for f in functions if f.error_conditions]) / len(functions)
        error_handling_score = error_handling_ratio * 100

        overall_score = (complexity_score + documentation_score + error_handling_score) / 3

        return {
            'overall_quality_score': round(overall_score, 2),
            'complexity_score': round(complexity_score, 2),
            'documentation_score': round(documentation_score, 2),
            'error_handling_score': round(error_handling_score, 2),
            'quality_grade': self._get_quality_grade(overall_score)
        }

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _calculate_testability_score(self, functions: List, test_opportunities: List) -> float:
        """Calculate testability score"""
        if not functions:
            return 0

        # Factors that improve testability
        pure_functions = len([f for f in functions if not f.has_state])
        documented_functions = len([f for f in functions if f.docstring])
        simple_functions = len([f for f in functions if f.complexity <= 5])

        # Calculate score
        testability_factors = [
            pure_functions / len(functions),  # Pure functions are easier to test
            documented_functions / len(functions),  # Documentation helps understand expected behavior
            simple_functions / len(functions),  # Simple functions are easier to test
        ]

        return round(sum(testability_factors) / len(testability_factors) * 100, 2)

    def _assess_overall_quality(self, data: Dict[str, Any]) -> str:
        """Assess overall code quality"""
        quality_metrics = self._calculate_quality_metrics(data)

        if not quality_metrics:
            return "Insufficient data for quality assessment"

        overall_score = quality_metrics.get('overall_quality_score', 0)

        if overall_score >= 90:
            return "Excellent - High quality code with good practices"
        elif overall_score >= 80:
            return "Good - Well-structured code with minor improvements needed"
        elif overall_score >= 70:
            return "Fair - Adequate code quality with some areas for improvement"
        elif overall_score >= 60:
            return "Poor - Significant improvements needed"
        else:
            return "Critical - Major refactoring required"

    def _assess_risks(self, data: Dict[str, Any]) -> List[str]:
        """Assess potential risks based on analysis"""
        risks = []

        source_analysis = data.get('source_analysis', {})
        complexity_metrics = source_analysis.get('complexity_metrics', {})

        # Complexity risks
        high_complexity_funcs = complexity_metrics.get('high_complexity_functions', [])
        if len(high_complexity_funcs) > 0:
            risks.append(f"High complexity functions ({len(high_complexity_funcs)}) increase maintenance risk")

        # Documentation risks
        functions = source_analysis.get('functions', [])
        if functions:
            undocumented_ratio = len([f for f in functions if not f.docstring]) / len(functions)
            if undocumented_ratio > 0.5:
                risks.append("Poor documentation coverage increases knowledge transfer risk")

        # Error handling risks
        if functions:
            no_error_handling_ratio = len([f for f in functions if not f.error_conditions]) / len(functions)
            if no_error_handling_ratio > 0.7:
                risks.append("Inadequate error handling increases system reliability risk")

        return risks

    def _create_function_details_appendix(self, data: Dict[str, Any]) -> List[Dict]:
        """Create detailed function information appendix"""
        functions = data.get('source_analysis', {}).get('functions', [])

        return [
            {
                'name': func.name,
                'language': func.language,
                'complexity': func.complexity,
                'parameters': func.parameters,
                'return_type': func.return_type,
                'has_documentation': bool(func.docstring),
                'error_conditions': func.error_conditions,
                'line_number': func.line_number
            }
            for func in functions
        ]

    def _create_test_scenarios_appendix(self, data: Dict[str, Any]) -> List[Dict]:
        """Create test scenarios details appendix"""
        return data.get('test_scenarios', [])

    def _create_code_samples_appendix(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create code samples appendix"""
        generated_tests = data.get('generated_tests', {})

        samples = {}
        for func_test in generated_tests.get('function_tests', []):
            function_name = func_test.get('function', 'unknown')
            test_code = func_test.get('test_code', '')
            samples[function_name] = test_code

        return samples

    def _create_configuration_appendix(self) -> Dict[str, Any]:
        """Create configuration details appendix"""
        return {
            'supported_languages': list(self.config.supported_languages.keys()),
            'test_categories': self.config.test_categories,
            'max_tests_per_function': self.config.max_tests_per_function,
            'include_performance_tests': self.config.include_performance_tests,
            'include_security_tests': self.config.include_security_tests
        }
