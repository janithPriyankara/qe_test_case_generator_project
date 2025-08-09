#!/usr/bin/env python3
"""
Setup and demonstration script for MDTD Test Engine
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import MDTDTestEngine
from src.config import Config

async def setup_demo():
    """Set up and run a demonstration of the MDTD system"""

    print("AI-Assisted Model-Driven Test Development (MDTD) System")
    print("=" * 60)

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables")
        print("The system will use fallback examples instead of AI generation")
        print()

    # Load configuration
    config = Config()

    # Initialize the test engine
    engine = MDTDTestEngine(config)

    # Test with the example Python file
    example_file = Path("examples/sample_python.py")

    if example_file.exists():
        print(f"Analyzing: {example_file}")
        print("-" * 40)

        # Run the analysis and test generation
        result = await engine.analyze_and_generate_tests(example_file, "html")

        if result['success']:
            print("Analysis and test generation completed successfully!")
            print()

            # Display summary
            analysis = result['analysis']
            print("SUMMARY:")
            print(f"   - Functions analyzed: {len(analysis.get('functions', []))}")
            print(f"   - Classes found: {len(analysis.get('classes', []))}")
            print(f"   - Test scenarios generated: {len(result.get('scenarios', []))}")
            print(f"   - Language distribution: {analysis.get('language_distribution', {})}")

            # Create timestamped output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"generated_{timestamp}")
            output_dir.mkdir(exist_ok=True)

            print(f"\nCreating output directory: {output_dir}")

            # Save HTML interface
            html_file = output_dir / "test_interface.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result['web_interface'])

            # Save analysis results
            import json
            analysis_file = output_dir / "source_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                # Convert dataclass objects to dict for JSON serialization
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
            scenarios_file = output_dir / "test_scenarios.json"
            with open(scenarios_file, 'w', encoding='utf-8') as f:
                json.dump(result.get('scenarios', []), f, indent=2, default=str)

            # Save generated tests
            tests_file = output_dir / "generated_tests.json"
            with open(tests_file, 'w', encoding='utf-8') as f:
                json.dump(result.get('tests', {}), f, indent=2, default=str)

            # Save web test cases separately
            web_tests_file = output_dir / "web_test_cases.json"
            if 'tests' in result and 'function_tests' in result['tests']:
                web_test_data = {}
                for func_test in result['tests']['function_tests']:
                    function_name = func_test.get('function', 'unknown')
                    web_test_data[function_name] = {
                        'test_code': func_test.get('test_code', ''),
                        'scenarios': func_test.get('scenarios', []),
                        'language': func_test.get('language', 'unknown')
                    }

                with open(web_tests_file, 'w', encoding='utf-8') as f:
                    json.dump(web_test_data, f, indent=2, default=str)

            # Create a simple report even if detailed report fails
            try:
                if result.get('report'):
                    report_file = output_dir / "detailed_report.json"
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(result['report'], f, indent=2, default=str)
            except Exception as e:
                print(f"Warning: Could not save detailed report: {str(e)}")

                # Create a simple summary report
                simple_report = {
                    'timestamp': datetime.now().isoformat(),
                    'summary': {
                        'functions_analyzed': len(analysis.get('functions', [])),
                        'classes_found': len(analysis.get('classes', [])),
                        'test_scenarios_generated': len(result.get('scenarios', [])),
                        'language_distribution': analysis.get('language_distribution', {}),
                        'complexity_metrics': analysis.get('complexity_metrics', {})
                    },
                    'files_generated': [
                        str(html_file.name),
                        str(analysis_file.name),
                        str(scenarios_file.name),
                        str(tests_file.name),
                        str(web_tests_file.name)
                    ]
                }

                summary_file = output_dir / "summary_report.json"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(simple_report, f, indent=2, default=str)

            print()
            print(f"Test interface saved to: {html_file}")
            print(f"Source analysis saved to: {analysis_file}")
            print(f"Test scenarios saved to: {scenarios_file}")
            print(f"Generated tests saved to: {tests_file}")
            print(f"Web test cases saved to: {web_tests_file}")
            print()
            print(f"All files are in directory: {output_dir}")
            print(f"Open {html_file} in your browser to run the interactive tests!")

        else:
            print(f"Error: {result['error']}")

    else:
        print(f"Example file not found: {example_file}")

def main():
    """Main entry point"""
    print("Setting up the MDTD Test Engineering system...")

    try:
        asyncio.run(setup_demo())
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
    except Exception as e:
        print(f"Setup failed: {str(e)}")

if __name__ == "__main__":
    main()
