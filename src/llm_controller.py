"""
LLM Controller for MDTD Test Engine
Manages communication with OpenAI API for intelligent test generation
"""

import json
import logging
from dataclasses import asdict
from typing import Dict, List, Any

import openai

from .config import Config
from .file_analyzer import FunctionInfo

logger = logging.getLogger(__name__)


class LLMController:
    """Controls LLM interactions for test generation"""

    def __init__(self, config: Config):
        self.config = config
        self.client = openai.AsyncOpenAI(api_key=config.openai_api_key)

    async def generate_comprehensive_tests(
        self,
        analysis_result: Dict[str, Any],
        test_scenarios: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive tests using LLM based on analysis and scenarios

        Args:
            analysis_result: Results from file analysis
            test_scenarios: MDTD test scenarios

        Returns:
            Generated test cases and code
        """
        try:
            logger.info("Starting LLM test generation...")

            # Generate tests for each function
            function_tests = []
            for function in analysis_result.get('functions', []):
                func_scenarios = [s for s in test_scenarios if s.get('function') == function.name]
                test_code = await self._generate_function_tests(function, func_scenarios)
                function_tests.append({
                    'function': function.name,
                    'language': function.language,
                    'test_code': test_code,
                    'scenarios': func_scenarios
                })

            # Generate integration tests
            integration_tests = await self._generate_integration_tests(analysis_result)

            # Generate performance tests
            performance_tests = await self._generate_performance_tests(analysis_result)

            # Generate security tests
            security_tests = await self._generate_security_tests(analysis_result)

            return {
                'function_tests': function_tests,
                'integration_tests': integration_tests,
                'performance_tests': performance_tests,
                'security_tests': security_tests,
                'summary': {
                    'total_functions_tested': len(function_tests),
                    'total_test_cases': sum(len(ft['scenarios']) for ft in function_tests),
                    'languages_covered': list(set(ft['language'] for ft in function_tests))
                }
            }

        except Exception as e:
            logger.error("Error in LLM test generation: {}".format(str(e)))
            raise

    async def _generate_function_tests(
        self,
        function: FunctionInfo,
        scenarios: List[Dict]
    ) -> str:
        """Generate test code for a specific function"""

        prompt = self._create_function_test_prompt(function, scenarios)

        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(function.language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.config.openai_max_tokens,
                temperature=self.config.openai_temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating tests for function {function.name}: {str(e)}")
            return self._get_fallback_test(function)

    def _create_function_test_prompt(self, function: FunctionInfo, scenarios: List[Dict]) -> str:
        """Create a detailed prompt for function test generation"""

        function_dict = asdict(function)

        prompt = f"""
Generate comprehensive test cases for the following function using MDTD principles:

FUNCTION DETAILS:
- Name: {function.name}
- Language: {function.language}
- Parameters: {json.dumps(function_dict['parameters'], indent=2)}
- Return Type: {function.return_type}
- Complexity: {function.complexity}
- Has State: {function.has_state}
- Error Conditions: {function.error_conditions}
- Documentation: {function.docstring or 'No documentation available'}

TEST SCENARIOS TO IMPLEMENT:
{json.dumps(scenarios, indent=2)}

REQUIREMENTS:
1. Create tests for HTML5 form inputs that can be executed in a web browser
2. Include equivalence partitioning tests
3. Include boundary value analysis tests
4. Include error condition tests
5. Include state transition tests if applicable
6. Generate both positive and negative test cases
7. Include performance considerations
8. Make tests suitable for display in HTML5 input fields

OUTPUT FORMAT:
Generate the response as a JSON object with the following structure:
{{
    "html_test_cases": [
        {{
            "test_id": "unique_id",
            "test_name": "descriptive_name",
            "category": "equivalence_partition|boundary_value|error_condition|state_transition",
            "input_html": "HTML5 input field code",
            "expected_output": "expected result",
            "test_data": "test input values",
            "validation_script": "JavaScript validation code"
        }}
    ],
    "test_summary": {{
        "total_tests": 0,
        "categories_covered": [],
        "complexity_score": 0
    }}
}}

Focus on creating tests that can be displayed and executed in a web interface with HTML5 input fields.
"""
        return prompt

    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on programming language"""
        base_prompt = """You are an expert software test engineer specializing in Model-Driven Test Development (MDTD). 
You create comprehensive, high-quality test cases that can be executed in web browsers using HTML5 forms.

Your expertise includes:
- Equivalence partitioning
- Boundary value analysis
- Error condition testing
- State transition testing
- Performance testing
- Security testing
- Web-based test interfaces

Always generate tests that are:
1. Comprehensive and cover edge cases
2. Suitable for HTML5 web interfaces
3. Include clear validation logic
4. Follow MDTD best practices
5. Include both positive and negative scenarios"""

        language_specific = {
            'python': "Focus on Python-specific testing patterns and data types.",
            'java': "Focus on Java-specific testing patterns, exceptions, and object-oriented concepts.",
            'cpp': "Focus on C++ memory management, pointers, and performance considerations.",
            'javascript': "Focus on JavaScript async patterns, DOM manipulation, and browser compatibility.",
            'csharp': "Focus on C# .NET patterns, exceptions, and type safety."
        }

        return base_prompt + "\n\n" + language_specific.get(language, "")

    async def _generate_integration_tests(self, analysis_result: Dict[str, Any]) -> List[Dict]:
        """Generate integration tests for multiple components"""

        functions = analysis_result.get('functions', [])
        if len(functions) < 2:
            return []

        prompt = f"""
Generate integration test scenarios for the following functions:
{json.dumps([{'name': f.name, 'parameters': f.parameters} for f in functions], indent=2)}

Create tests that verify:
1. Function interactions
2. Data flow between functions
3. End-to-end workflows
4. Error propagation

Output as JSON with HTML5-compatible test cases.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt('integration')},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            # Parse response and return structured data
            content = response.choices[0].message.content
            # Try to extract JSON from response
            try:
                return json.loads(content)
            except:
                return [{'test_name': 'Integration Test', 'description': content}]

        except Exception as e:
            logger.error(f"Error generating integration tests: {str(e)}")
            return []

    async def _generate_performance_tests(self, analysis_result: Dict[str, Any]) -> List[Dict]:
        """Generate performance test scenarios"""

        if not self.config.include_performance_tests:
            return []

        high_complexity_funcs = [
            f for f in analysis_result.get('functions', [])
            if f.complexity > 5
        ]

        if not high_complexity_funcs:
            return []

        prompt = f"""
Generate performance test scenarios for these high-complexity functions:
{json.dumps([{'name': f.name, 'complexity': f.complexity} for f in high_complexity_funcs], indent=2)}

Create tests that verify:
1. Execution time under normal load
2. Memory usage patterns
3. Scalability with large inputs
4. Resource cleanup

Output as JSON with HTML5-compatible test cases including timing measurements.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a performance testing expert. Create web-based performance tests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )

            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return [{'test_name': 'Performance Test', 'description': content}]

        except Exception as e:
            logger.error(f"Error generating performance tests: {str(e)}")
            return []

    async def _generate_security_tests(self, analysis_result: Dict[str, Any]) -> List[Dict]:
        """Generate security test scenarios"""

        if not self.config.include_security_tests:
            return []

        functions_with_inputs = [
            f for f in analysis_result.get('functions', [])
            if f.parameters and any(p.get('type') in ['string', 'str'] for p in f.parameters)
        ]

        if not functions_with_inputs:
            return []

        prompt = f"""
Generate security test scenarios for these functions that accept string inputs:
{json.dumps([{'name': f.name, 'parameters': f.parameters} for f in functions_with_inputs], indent=2)}

Create tests that verify protection against:
1. SQL injection attempts
2. XSS attacks
3. Buffer overflow attempts
4. Invalid input validation
5. Authentication bypass

Output as JSON with HTML5-compatible test cases.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are a security testing expert. Create web-based security tests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )

            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return [{'test_name': 'Security Test', 'description': content}]

        except Exception as e:
            logger.error(f"Error generating security tests: {str(e)}")
            return []

    def _get_fallback_test(self, function: FunctionInfo) -> str:
        """Generate a simple fallback test when LLM fails"""
        return f"""
{{
    "html_test_cases": [
        {{
            "test_id": "fallback_{function.name}",
            "test_name": "Basic {function.name} Test",
            "category": "equivalence_partition",
            "input_html": "<input type='text' id='input_{function.name}' placeholder='Enter test value'>",
            "expected_output": "Function should execute without errors",
            "test_data": "sample_input",
            "validation_script": "// Basic validation for {function.name}"
        }}
    ],
    "test_summary": {{
        "total_tests": 1,
        "categories_covered": ["basic"],
        "complexity_score": 1
    }}
}}
"""

    async def validate_api_connection(self) -> bool:
        """Validate OpenAI API connection"""
        try:
            await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"API validation failed: {str(e)}")
            return False
