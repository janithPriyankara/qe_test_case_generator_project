# AI-Assisted Model-Driven Test Development (MDTD) Prototype

A Python-based system that analyzes source code in multiple programming languages and automatically generates comprehensive test cases using AI, creating interactive HTML5 web interfaces for test execution.

## Features

- **Multi-Language Source Analysis**: Analyzes Python, Java, C++, C#, JavaScript files
- **AI-Powered Test Generation**: Uses OpenAI GPT-4 to create comprehensive test cases
- **MDTD Methodology**: Implements Model-Driven Test Development principles:
  - Equivalence Partitioning
  - Boundary Value Analysis  
  - Error Condition Testing
  - State Transition Testing
- **Interactive HTML5 Interfaces**: Creates beautiful web-based test execution environments
- **Comprehensive Reporting**: Detailed code quality analysis and recommendations
- **Timestamped Output**: Organized results in `generated_YYYYMMDD_HHMMSS` directories

## Prerequisites

- Python 3.7 or higher
- OpenAI API key
- Web browser (for viewing generated test interfaces)

## Installation

1. Clone or download this project
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   # Windows (Command Prompt)
   set OPENAI_API_KEY=your_api_key_here
   
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your_api_key_here"
   
   # Linux/Mac
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

Analyze any source file:
```bash
python main.py path/to/your/source_file.py
```

Or run the demo:
```bash
python setup_demo.py
```

### Example Usage

```bash
# Analyze Python files
python main.py examples/sample_python.py

# Analyze Java files  
python main.py examples/Calculator.java

# Analyze entire projects
python main.py /path/to/your/project --output my_tests
```

## Generated Output

Each run creates a timestamped directory (`generated_YYYYMMDD_HHMMSS`) containing:

- **`test_interface.html`** - Interactive web-based test execution interface
- **`source_analysis.json`** - Detailed source code analysis results
- **`test_scenarios.json`** - MDTD test scenarios generated
- **`generated_tests.json`** - AI-generated test code
- **`web_test_cases.json`** - Web-formatted test cases
- **`detailed_report.json`** - Comprehensive quality and testing report

## Interactive Web Testing

1. Navigate to your generated directory
2. Open `test_interface.html` in your web browser
3. Use the interactive interface to:
   - Execute individual test cases
   - Fill in test values using HTML5 input fields
   - View real-time results with charts and statistics
   - Run comprehensive test suites

## Project Structure

```
QeTestCaseGenerator/
├── main.py                     # Main MDTD application
├── setup_demo.py              # Demo script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── src/                       # Core Python modules
│   ├── config.py             # Configuration management
│   ├── file_analyzer.py      # Multi-language source analysis
│   ├── llm_controller.py     # OpenAI API integration
│   ├── test_generator.py     # HTML5 test case generation
│   ├── web_interface.py      # Interactive web interface creation
│   └── report_generator.py   # Comprehensive reporting
├── examples/                  # Sample source files
│   ├── sample_python.py      # Python examples
│   └── Calculator.java       # Java examples
└── generated_*/              # Generated test results (timestamped)
    ├── test_interface.html   # Interactive web interface
    ├── source_analysis.json  # Code analysis
    └── ...                   # Other generated files
```

## MDTD Test Categories

The system generates comprehensive test cases using proven MDTD methodologies:

1. **Equivalence Partitioning**: Tests for valid/invalid input classes
2. **Boundary Value Analysis**: Tests at input boundaries and limits
3. **Error Condition Testing**: Tests for proper error handling
4. **Performance Testing**: Tests for execution time and resource usage
5. **Security Testing**: Tests for common security vulnerabilities

## Supported Languages

- **Python** (.py)
- **Java** (.java)
- **C++** (.cpp, .cc, .cxx, .c++)
- **C** (.c)
- **JavaScript** (.js, .ts)
- **C#** (.cs)

## Configuration

The system uses smart defaults but can be customized via `src/config.py`:

- Maximum tests per function
- Test categories to include
- Output formats
- Language-specific settings

## API Usage

The system consumes OpenAI GPT-4 tokens for test generation:
- Average: 1000-2000 tokens per function
- Estimated cost: $0.03-0.06 per function analyzed

## Requirements

See `requirements.txt` for the minimal dependency list:
- `openai>=1.12.0` - GPT-4 API integration
- `javalang>=0.15.0` - Java source parsing

All other dependencies are Python built-ins.

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**: Verify your OPENAI_API_KEY environment variable
2. **"Module not found" error**: Run `pip install -r requirements.txt`
3. **"Permission denied" errors**: Ensure write permissions in project directory

### Getting Help

1. Check error messages for specific guidance
2. Verify API key and internet connection
3. Ensure source files are valid and accessible
4. Try the demo first: `python setup_demo.py`

## License

MIT License - Free to use and modify for your testing needs.
