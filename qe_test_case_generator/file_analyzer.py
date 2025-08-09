"""
Multi-language source file analyzer for MDTD Test Engine
Analyzes source code in various programming languages to extract testable components
"""

import ast
import re
import javalang
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Information about a function extracted from source code"""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    line_number: int
    language: str
    visibility: str = 'public'
    is_static: bool = False
    has_state: bool = False
    error_conditions: List[str] = None

    def __post_init__(self):
        if self.error_conditions is None:
            self.error_conditions = []


@dataclass
class ClassInfo:
    """Information about a class extracted from source code"""
    name: str
    methods: List[FunctionInfo]
    attributes: List[Dict[str, Any]]
    inheritance: List[str]
    language: str
    line_number: int


class FileAnalyzer:
    """Analyzes source files in multiple programming languages"""

    def __init__(self, config: Config):
        self.config = config
        self.analyzers = {
            'python': self._analyze_python,
            'java': self._analyze_java,
            'cpp': self._analyze_cpp,
            'c': self._analyze_c,
            'javascript': self._analyze_javascript,
            'csharp': self._analyze_csharp
        }

    async def analyze(self, source_path: Path) -> Dict[str, Any]:
        """
        Analyze source file(s) and extract testable components

        Args:
            source_path: Path to source file or directory

        Returns:
            Dictionary containing analysis results
        """
        results = {
            'files': [],
            'functions': [],
            'classes': [],
            'complexity_metrics': {},
            'test_opportunities': [],
            'language_distribution': {}
        }

        if source_path.is_file():
            file_results = await self._analyze_file(source_path)
            if file_results:
                results['files'].append(file_results)
                self._merge_results(results, file_results)
        else:
            # Analyze directory recursively
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    extension = file_path.suffix
                    language = self.config.get_language_for_extension(extension)
                    if language:
                        file_results = await self._analyze_file(file_path)
                        if file_results:
                            results['files'].append(file_results)
                            self._merge_results(results, file_results)

        # Calculate additional metrics
        results['complexity_metrics'] = self._calculate_complexity_metrics(results)
        results['test_opportunities'] = self._identify_test_opportunities(results)

        return results

    async def _analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single source file"""
        try:
            extension = file_path.suffix
            language = self.config.get_language_for_extension(extension)

            if not language or language not in self.analyzers:
                logger.warning(f"Unsupported language for file: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            analyzer = self.analyzers[language]
            analysis = analyzer(content, str(file_path))

            analysis['file_path'] = str(file_path)
            analysis['language'] = language
            analysis['file_size'] = len(content)
            analysis['line_count'] = len(content.splitlines())

            logger.info(f"Analyzed {language} file: {file_path}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return None

    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python source code"""
        try:
            tree = ast.parse(content)
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_python_function(node, content)
                    functions.append(func_info)
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node, content)
                    classes.append(class_info)

            return {
                'functions': functions,
                'classes': classes,
                'imports': self._extract_python_imports(tree),
                'global_variables': self._extract_python_globals(tree)
            }

        except SyntaxError as e:
            logger.error(f"Python syntax error in {file_path}: {str(e)}")
            return {'functions': [], 'classes': [], 'imports': [], 'global_variables': []}

    def _extract_python_function(self, node: ast.FunctionDef, content: str) -> FunctionInfo:
        """Extract function information from Python AST node"""
        parameters = []

        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_python_type_hint(arg),
                'default': None,
                'required': True
            }
            parameters.append(param_info)

        # Handle default arguments
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                param_index = len(parameters) - len(defaults) + i
                if param_index >= 0:
                    parameters[param_index]['default'] = ast.unparse(default)
                    parameters[param_index]['required'] = False

        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        docstring = ast.get_docstring(node)
        complexity = self._calculate_cyclomatic_complexity(node)

        # Check for error handling
        error_conditions = self._extract_error_conditions(node)

        return FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            complexity=complexity,
            line_number=node.lineno,
            language='python',
            error_conditions=error_conditions,
            has_state=self._has_state_modifications(node)
        )

    def _extract_python_class(self, node: ast.ClassDef, content: str) -> ClassInfo:
        """Extract class information from Python AST node"""
        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_python_function(item, content)
                methods.append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append({
                            'name': target.id,
                            'type': 'unknown',
                            'line_number': item.lineno
                        })

        inheritance = [ast.unparse(base) for base in node.bases]

        return ClassInfo(
            name=node.name,
            methods=methods,
            attributes=attributes,
            inheritance=inheritance,
            language='python',
            line_number=node.lineno
        )

    def _analyze_java(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Java source code"""
        try:
            tree = javalang.parse.parse(content)
            functions = []
            classes = []

            for path, node in tree.filter(javalang.tree.MethodDeclaration):
                func_info = self._extract_java_function(node)
                functions.append(func_info)

            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = self._extract_java_class(node)
                classes.append(class_info)

            return {
                'functions': functions,
                'classes': classes,
                'imports': self._extract_java_imports(tree),
                'package': getattr(tree.package, 'name', '') if tree.package else ''
            }

        except Exception as e:
            logger.error(f"Java parsing error in {file_path}: {str(e)}")
            return {'functions': [], 'classes': [], 'imports': [], 'package': ''}

    def _extract_java_function(self, node) -> FunctionInfo:
        """Extract function information from Java AST node"""
        parameters = []

        if node.parameters:
            for param in node.parameters:
                param_info = {
                    'name': param.name,
                    'type': str(param.type.name) if hasattr(param.type, 'name') else str(param.type),
                    'required': True
                }
                parameters.append(param_info)

        return_type = str(node.return_type.name) if node.return_type and hasattr(node.return_type, 'name') else 'void'

        # Fix position attribute access
        line_number = node.position.line if hasattr(node, 'position') else 0

        return FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=None,  # Java doesn't have docstrings like Python
            complexity=1,  # Simplified for now
            line_number=line_number,
            language='java',
            visibility='public' if 'public' in (node.modifiers or []) else 'private',
            is_static='static' in (node.modifiers or [])
        )

    def _extract_java_class(self, node) -> ClassInfo:
        """Extract class information from Java AST node"""
        methods = []
        attributes = []

        # Extract methods
        for method in node.methods or []:
            method_info = self._extract_java_function(method)
            methods.append(method_info)

        # Extract fields
        for field in node.fields or []:
            for declarator in field.declarators:
                attributes.append({
                    'name': declarator.name,
                    'type': str(field.type.name) if hasattr(field.type, 'name') else str(field.type),
                    'line_number': field.position.line if hasattr(field, 'position') else 0
                })

        inheritance = []
        if node.extends:
            inheritance.append(str(node.extends.name))
        if node.implements:
            inheritance.extend([str(impl.name) for impl in node.implements])

        # Fix position attribute access
        line_number = node.position.line if hasattr(node, 'position') else 0

        return ClassInfo(
            name=node.name,
            methods=methods,
            attributes=attributes,
            inheritance=inheritance,
            language='java',
            line_number=line_number
        )

    def _analyze_cpp(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze C++ source code using regex patterns"""
        functions = []
        classes = []

        # Simple regex-based analysis for C++
        function_pattern = r'(?:(\w+)\s+)?(\w+)\s*\([^)]*\)\s*{'
        class_pattern = r'class\s+(\w+)(?:\s*:\s*[^{]+)?\s*{'

        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # Find functions
            func_match = re.search(function_pattern, line)
            if func_match:
                return_type = func_match.group(1) or 'void'
                func_name = func_match.group(2)

                if func_name not in ['if', 'while', 'for', 'switch']:  # Filter out control structures
                    func_info = FunctionInfo(
                        name=func_name,
                        parameters=[],  # Simplified - would need proper parser
                        return_type=return_type,
                        docstring=None,
                        complexity=1,
                        line_number=i,
                        language='cpp'
                    )
                    functions.append(func_info)

            # Find classes
            class_match = re.search(class_pattern, line)
            if class_match:
                class_name = class_match.group(1)
                class_info = ClassInfo(
                    name=class_name,
                    methods=[],
                    attributes=[],
                    inheritance=[],
                    language='cpp',
                    line_number=i
                )
                classes.append(class_info)

        return {
            'functions': functions,
            'classes': classes,
            'includes': self._extract_cpp_includes(content)
        }

    def _analyze_c(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze C source code"""
        # Similar to C++ but simpler
        return self._analyze_cpp(content, file_path)

    def _analyze_javascript(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript source code using regex patterns"""
        functions = []

        # Regex patterns for different function declarations
        patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',  # function name() {}
            r'(\w+)\s*=\s*function\s*\([^)]*\)\s*{',  # name = function() {}
            r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{',  # name: function() {}
            r'(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # name = () => {}
        ]

        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    func_info = FunctionInfo(
                        name=func_name,
                        parameters=[],  # Simplified
                        return_type='unknown',
                        docstring=None,
                        complexity=1,
                        line_number=i,
                        language='javascript'
                    )
                    functions.append(func_info)
                    break

        return {
            'functions': functions,
            'classes': [],
            'imports': self._extract_js_imports(content)
        }

    def _analyze_csharp(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze C# source code using regex patterns"""
        functions = []
        classes = []

        # C# method pattern
        method_pattern = r'(?:public|private|protected|internal)?\s*(?:static)?\s*(\w+)\s+(\w+)\s*\([^)]*\)\s*{'
        class_pattern = r'(?:public|private|protected|internal)?\s*class\s+(\w+)(?:\s*:\s*[^{]+)?\s*{'

        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # Find methods
            method_match = re.search(method_pattern, line)
            if method_match:
                return_type = method_match.group(1)
                method_name = method_match.group(2)

                func_info = FunctionInfo(
                    name=method_name,
                    parameters=[],
                    return_type=return_type,
                    docstring=None,
                    complexity=1,
                    line_number=i,
                    language='csharp'
                )
                functions.append(func_info)

            # Find classes
            class_match = re.search(class_pattern, line)
            if class_match:
                class_name = class_match.group(1)
                class_info = ClassInfo(
                    name=class_name,
                    methods=[],
                    attributes=[],
                    inheritance=[],
                    language='csharp',
                    line_number=i
                )
                classes.append(class_info)

        return {
            'functions': functions,
            'classes': classes,
            'usings': self._extract_csharp_usings(content)
        }

    # Helper methods
    def _get_python_type_hint(self, arg) -> Optional[str]:
        """Extract type hint from Python function argument"""
        if hasattr(arg, 'annotation') and arg.annotation:
            return ast.unparse(arg.annotation)
        return None

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _extract_error_conditions(self, node) -> List[str]:
        """Extract potential error conditions from function"""
        conditions = []
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc and isinstance(child.exc, ast.Call):
                    if hasattr(child.exc.func, 'id'):
                        conditions.append(child.exc.func.id)
        return conditions

    def _has_state_modifications(self, node) -> bool:
        """Check if function modifies state"""
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute):
                        return True
        return False

    def _extract_python_imports(self, tree) -> List[str]:
        """Extract import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _extract_python_globals(self, tree) -> List[str]:
        """Extract global variables"""
        globals_vars = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_vars.append(target.id)
        return globals_vars

    def _extract_java_imports(self, tree) -> List[str]:
        """Extract Java imports"""
        imports = []
        if hasattr(tree, 'imports') and tree.imports:
            for imp in tree.imports:
                imports.append(imp.path)
        return imports

    def _extract_cpp_includes(self, content: str) -> List[str]:
        """Extract C++ includes"""
        includes = []
        for line in content.splitlines():
            match = re.match(r'#include\s*[<"]([^>"]+)[>"]', line)
            if match:
                includes.append(match.group(1))
        return includes

    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript imports"""
        imports = []
        patterns = [
            r'import\s+.*\s+from\s+["\']([^"\']+)["\']',
            r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'
        ]

        for line in content.splitlines():
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    imports.append(match.group(1))
        return imports

    def _extract_csharp_usings(self, content: str) -> List[str]:
        """Extract C# using statements"""
        usings = []
        for line in content.splitlines():
            match = re.match(r'using\s+([^;]+);', line)
            if match:
                usings.append(match.group(1))
        return usings

    def _merge_results(self, main_results: Dict, file_results: Dict):
        """Merge file analysis results into main results"""
        main_results['functions'].extend(file_results.get('functions', []))
        main_results['classes'].extend(file_results.get('classes', []))

        # Update language distribution
        language = file_results.get('language', 'unknown')
        main_results['language_distribution'][language] = \
            main_results['language_distribution'].get(language, 0) + 1

    def _calculate_complexity_metrics(self, results: Dict) -> Dict:
        """Calculate overall complexity metrics"""
        functions = results['functions']
        if not functions:
            return {}

        complexities = [f.complexity for f in functions]

        return {
            'total_functions': len(functions),
            'average_complexity': sum(complexities) / len(complexities),
            'max_complexity': max(complexities),
            'high_complexity_functions': [
                f.name for f in functions if f.complexity > 10
            ]
        }

    def _identify_test_opportunities(self, results: Dict) -> List[Dict]:
        """Identify testing opportunities based on analysis"""
        opportunities = []

        for func in results['functions']:
            # High complexity functions need more testing
            if func.complexity > 5:
                opportunities.append({
                    'type': 'high_complexity',
                    'function': func.name,
                    'priority': 'high',
                    'reason': f'Cyclomatic complexity: {func.complexity}'
                })

            # Functions with error conditions
            if func.error_conditions:
                opportunities.append({
                    'type': 'error_handling',
                    'function': func.name,
                    'priority': 'medium',
                    'reason': f'Error conditions: {", ".join(func.error_conditions)}'
                })

            # Functions with state modifications
            if func.has_state:
                opportunities.append({
                    'type': 'state_testing',
                    'function': func.name,
                    'priority': 'medium',
                    'reason': 'Function modifies state'
                })

        return opportunities
