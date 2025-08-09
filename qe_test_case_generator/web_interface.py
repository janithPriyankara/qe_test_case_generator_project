"""
Web Interface Generator for MDTD Test Engine
Creates HTML5 web interfaces for interactive test execution
"""

import json
from typing import Dict, List, Any
from datetime import datetime
import logging

from .config import Config

logger = logging.getLogger(__name__)


class WebInterface:
    """Creates interactive web interfaces for test execution"""

    def __init__(self, config: Config):
        self.config = config

    async def create_test_interface(self, web_test_cases: Dict[str, Any]) -> str:
        """
        Create a complete HTML5 interface for test execution

        Args:
            web_test_cases: Web-compatible test cases from TestGenerator

        Returns:
            Complete HTML page as string
        """
        try:
            logger.info("Creating HTML5 test interface...")

            # Generate HTML components
            html_head = self._generate_html_head()
            html_body = self._generate_html_body(web_test_cases)
            css_styles = self._generate_css_styles()
            javascript_code = self._generate_javascript_code()

            # Combine into complete HTML page
            complete_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    {html_head}
    <style>
        {css_styles}
    </style>
</head>
<body>
    {html_body}
    
    <script>
        {javascript_code}
    </script>
</body>
</html>
"""

            logger.info("HTML5 interface created successfully")
            return complete_html

        except Exception as e:
            logger.error("Error creating web interface: {}".format(str(e)))
            raise

    def _generate_html_head(self) -> str:
        """Generate HTML head section"""
        return """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Assisted MDTD Test Engineering Interface</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Chart.js for visualizations -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Highlight.js for code syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js"></script>
    
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
"""

    def _generate_html_body(self, web_test_cases: Dict[str, Any]) -> str:
        """Generate HTML body with test interface"""

        metadata = web_test_cases.get('metadata', {})
        test_suites = web_test_cases.get('test_suites', [])

        # Generate navigation
        navigation = self._generate_navigation(test_suites)

        # Generate dashboard
        dashboard = self._generate_dashboard(metadata, test_suites)

        # Generate test suites
        test_suites_html = self._generate_test_suites_html(test_suites)

        # Generate results panel
        results_panel = self._generate_results_panel()

        return f"""
    <div class="container-fluid">
        <!-- Header -->
        <header class="bg-primary text-white py-3 mb-4">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col">
                        <h1 class="mb-0">
                            <i class="fas fa-robot me-2"></i>
                            AI-Assisted MDTD Test Engineering
                        </h1>
                        <p class="mb-0 opacity-75">Model-Driven Test Development Interface</p>
                    </div>
                    <div class="col-auto">
                        <button class="btn btn-light" onclick="exportResults()">
                            <i class="fas fa-download me-1"></i> Export Results
                        </button>
                    </div>
                </div>
            </div>
        </header>
        
        <!-- Navigation -->
        {navigation}
        
        <!-- Main Content -->
        <div class="container">
            <div class="row">
                <!-- Sidebar -->
                <div class="col-md-3">
                    {dashboard}
                </div>
                
                <!-- Test Content -->
                <div class="col-md-9">
                    {test_suites_html}
                </div>
            </div>
        </div>
        
        <!-- Results Panel -->
        {results_panel}
        
        <!-- Footer -->
        <footer class="bg-dark text-white text-center py-3 mt-5">
            <p class="mb-0">Generated on {metadata.get('generated_at', datetime.now().isoformat())}</p>
        </footer>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
"""

    def _generate_navigation(self, test_suites: List[Dict]) -> str:
        """Generate navigation menu"""

        nav_items = []
        for suite in test_suites:
            suite_id = suite.get('suite_id', '')
            suite_name = suite.get('suite_name', 'Unknown Suite')
            test_count = suite.get('test_count', 0)

            nav_items.append(f"""
                <li class="nav-item">
                    <a class="nav-link" href="#suite-{suite_id}" onclick="showTestSuite('{suite_id}')">
                        {suite_name} <span class="badge bg-secondary">{test_count}</span>
                    </a>
                </li>
            """)

        return f"""
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="#dashboard" onclick="showDashboard()">
                            <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                        </a>
                    </li>
                    {''.join(nav_items)}
                    <li class="nav-item">
                        <a class="nav-link" href="#results" onclick="showResults()">
                            <i class="fas fa-chart-bar me-1"></i> Results
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
"""

    def _generate_dashboard(self, metadata: Dict, test_suites: List[Dict]) -> str:
        """Generate dashboard with statistics"""

        total_tests = sum(suite.get('test_count', 0) for suite in test_suites)
        languages = list(set(suite.get('language', 'unknown') for suite in test_suites if suite.get('language')))
        categories = []
        for suite in test_suites:
            categories.extend(suite.get('categories', []))
        unique_categories = list(set(categories))

        return f"""
        <div class="card mb-4" id="dashboard">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-info-circle me-2"></i>Test Overview
                </h5>
            </div>
            <div class="card-body">
                <div class="row text-center mb-3">
                    <div class="col">
                        <div class="border rounded p-2">
                            <h3 class="text-primary mb-0">{len(test_suites)}</h3>
                            <small>Test Suites</small>
                        </div>
                    </div>
                    <div class="col">
                        <div class="border rounded p-2">
                            <h3 class="text-success mb-0">{total_tests}</h3>
                            <small>Total Tests</small>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <h6>Languages Detected:</h6>
                    <div class="d-flex flex-wrap gap-1">
                        {' '.join(f'<span class="badge bg-primary">{lang}</span>' for lang in languages)}
                    </div>
                </div>
                
                <div class="mb-3">
                    <h6>Test Categories:</h6>
                    <div class="d-flex flex-wrap gap-1">
                        {' '.join(f'<span class="badge bg-secondary">{cat}</span>' for cat in unique_categories)}
                    </div>
                </div>
                
                <div class="d-grid gap-2">
                    <button class="btn btn-success" onclick="runAllTests()">
                        <i class="fas fa-play me-1"></i> Run All Tests
                    </button>
                    <button class="btn btn-outline-primary" onclick="generateReport()">
                        <i class="fas fa-file-alt me-1"></i> Generate Report
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Progress Card -->
        <div class="card mb-4" id="progress-card" style="display: none;">
            <div class="card-header">
                <h6 class="mb-0">Test Execution Progress</h6>
            </div>
            <div class="card-body">
                <div class="progress mb-2">
                    <div class="progress-bar" role="progressbar" id="progress-bar" style="width: 0%"></div>
                </div>
                <div class="d-flex justify-content-between">
                    <span id="progress-text">Ready to start</span>
                    <span id="progress-percentage">0%</span>
                </div>
            </div>
        </div>
"""

    def _generate_test_suites_html(self, test_suites: List[Dict]) -> str:
        """Generate HTML for all test suites"""

        suites_html = []

        for suite in test_suites:
            suite_html = self._generate_single_test_suite(suite)
            suites_html.append(suite_html)

        return ''.join(suites_html)

    def _generate_single_test_suite(self, suite: Dict) -> str:
        """Generate HTML for a single test suite"""

        suite_id = suite.get('suite_id', '')
        suite_name = suite.get('suite_name', 'Test Suite')
        function_name = suite.get('function_name', '')
        language = suite.get('language', 'unknown')
        test_count = suite.get('test_count', 0)
        html_forms = suite.get('html_forms', [])

        # Generate test forms
        forms_html = []
        for form_data in html_forms:
            forms_html.append(form_data.get('html', ''))

        return f"""
        <div class="test-suite-container mb-5" id="suite-{suite_id}" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <div class="row align-items-center">
                        <div class="col">
                            <h4 class="mb-0">{suite_name}</h4>
                            <div class="mt-1">
                                <span class="badge bg-info me-2">{language}</span>
                                <span class="badge bg-secondary">{test_count} tests</span>
                                {f'<span class="badge bg-success">Function: {function_name}</span>' if function_name else ''}
                            </div>
                        </div>
                        <div class="col-auto">
                            <div class="btn-group">
                                <button class="btn btn-outline-primary btn-sm" onclick="runSuiteTests('{suite_id}')">
                                    <i class="fas fa-play me-1"></i> Run Suite
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="resetSuite('{suite_id}')">
                                    <i class="fas fa-undo me-1"></i> Reset
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card-body">
                    <div class="test-cases-container">
                        {''.join(forms_html)}
                    </div>
                </div>
            </div>
        </div>
"""

    def _generate_results_panel(self) -> str:
        """Generate results panel for displaying test outcomes"""
        return """
        <div class="results-panel" id="results-panel" style="display: none;">
            <div class="container mt-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-chart-bar me-2"></i>Test Results Summary
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <canvas id="resultsChart"></canvas>
                            </div>
                            <div class="col-md-6">
                                <div class="results-statistics">
                                    <div class="row text-center">
                                        <div class="col-4">
                                            <div class="border rounded p-3 bg-success text-white">
                                                <h3 id="passed-count">0</h3>
                                                <small>Passed</small>
                                            </div>
                                        </div>
                                        <div class="col-4">
                                            <div class="border rounded p-3 bg-danger text-white">
                                                <h3 id="failed-count">0</h3>
                                                <small>Failed</small>
                                            </div>
                                        </div>
                                        <div class="col-4">
                                            <div class="border rounded p-3 bg-warning text-white">
                                                <h3 id="skipped-count">0</h3>
                                                <small>Skipped</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="detailed-results">
                            <h6>Detailed Results:</h6>
                            <div class="table-responsive">
                                <table class="table table-striped" id="results-table">
                                    <thead>
                                        <tr>
                                            <th>Test Name</th>
                                            <th>Category</th>
                                            <th>Status</th>
                                            <th>Execution Time</th>
                                            <th>Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <!-- Results will be populated here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

    def _generate_css_styles(self) -> str:
        """Generate CSS styles for the interface"""
        return """
        /* Custom styles for MDTD Test Interface */
        
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .test-case-container {
            border: 1px solid #dee2e6;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 2rem;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease;
        }
        
        .test-case-container:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .test-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #eee;
        }
        
        .test-title {
            color: #2c3e50;
            margin: 0;
            font-size: 1.2rem;
        }
        
        .test-category {
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
        }
        
        .badge-equivalence_partition { background-color: #007bff; }
        .badge-boundary_value { background-color: #28a745; }
        .badge-error_condition { background-color: #dc3545; }
        .badge-performance { background-color: #ffc107; color: #212529; }
        .badge-security { background-color: #6f42c1; }
        .badge-general { background-color: #6c757d; }
        
        .input-section, .expected-output-section {
            margin-bottom: 1.5rem;
        }
        
        .input-section h4, .expected-output-section h4 {
            color: #495057;
            font-size: 1rem;
            margin-bottom: 0.75rem;
            border-left: 3px solid #007bff;
            padding-left: 0.5rem;
        }
        
        .input-group {
            margin-bottom: 1rem;
        }
        
        .input-group label {
            font-weight: 500;
            color: #495057;
            margin-bottom: 0.25rem;
        }
        
        .form-control {
            border-radius: 0.375rem;
            border: 1px solid #ced4da;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        
        .form-control:focus {
            border-color: #80bdff;
            box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }
        
        .expected-output {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 0.375rem;
            padding: 0.75rem;
            font-family: monospace;
            color: #495057;
        }
        
        .action-buttons {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .test-results {
            background-color: #f8f9fa;
            border-radius: 0.375rem;
            padding: 1rem;
            border-left: 4px solid #007bff;
        }
        
        .test-results.success {
            border-left-color: #28a745;
            background-color: #d4edda;
        }
        
        .test-results.failure {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }
        
        .result-content {
            font-family: monospace;
            white-space: pre-wrap;
            color: #495057;
        }
        
        .test-suite-container {
            margin-bottom: 2rem;
        }
        
        .progress {
            height: 0.5rem;
        }
        
        .navbar-brand {
            font-weight: bold;
        }
        
        .results-statistics .border {
            transition: transform 0.2s ease;
        }
        
        .results-statistics .border:hover {
            transform: translateY(-2px);
        }
        
        #results-table {
            font-size: 0.9rem;
        }
        
        .status-passed {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-failed {
            color: #dc3545;
            font-weight: bold;
        }
        
        .status-skipped {
            color: #ffc107;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .test-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .action-buttons .btn {
                margin-bottom: 0.5rem;
            }
        }
        
        /* Animation for test execution */
        .test-running {
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* Loading spinner */
        .spinner {
            border: 2px solid #f3f3f3;
            border-top: 2px solid #007bff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
"""

    def _generate_javascript_code(self) -> str:
        """Generate JavaScript code for interface functionality"""
        return """
        // Global variables
        let testResults = [];
        let currentSuite = null;
        let executionStats = {
            passed: 0,
            failed: 0,
            skipped: 0,
            total: 0
        };
        
        // Initialize the interface
        document.addEventListener('DOMContentLoaded', function() {
            showDashboard();
            initializeCharts();
            hljs.highlightAll();
        });
        
        // Navigation functions
        function showDashboard() {
            hideAllSections();
            document.getElementById('dashboard').style.display = 'block';
            setActiveNavItem('dashboard');
        }
        
        function showTestSuite(suiteId) {
            hideAllSections();
            document.getElementById(`suite-${suiteId}`).style.display = 'block';
            currentSuite = suiteId;
        }
        
        function showResults() {
            hideAllSections();
            document.getElementById('results-panel').style.display = 'block';
            updateResultsChart();
        }
        
        function hideAllSections() {
            // Hide dashboard
            const dashboard = document.getElementById('dashboard');
            if (dashboard) dashboard.style.display = 'none';
            
            // Hide all test suites
            const suites = document.querySelectorAll('.test-suite-container');
            suites.forEach(suite => suite.style.display = 'none');
            
            // Hide results panel
            const results = document.getElementById('results-panel');
            if (results) results.style.display = 'none';
        }
        
        function setActiveNavItem(itemId) {
            // Remove active class from all nav items
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // Add active class to current item
            const activeLink = document.querySelector(`a[href="#${itemId}"]`);
            if (activeLink) activeLink.classList.add('active');
        }
        
        // Test execution functions
        function executeTest(testId, event) {
            if (event) event.preventDefault();
            
            const testContainer = document.getElementById(`test-${testId}`);
            const resultsDiv = document.getElementById(`results-${testId}`);
            
            if (!testContainer || !resultsDiv) {
                console.error(`Test elements not found for ID: ${testId}`);
                return false;
            }
            
            // Show loading state
            testContainer.classList.add('test-running');
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="spinner"></div>Executing test...';
            
            // Simulate test execution with delay
            setTimeout(() => {
                try {
                    const result = performTestExecution(testId);
                    displayTestResult(testId, result);
                    updateExecutionStats(result);
                } catch (error) {
                    const errorResult = {
                        success: false,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    };
                    displayTestResult(testId, errorResult);
                    updateExecutionStats(errorResult);
                } finally {
                    testContainer.classList.remove('test-running');
                }
            }, 1000 + Math.random() * 2000); // Random delay 1-3 seconds
            
            return false;
        }
        
        function performTestExecution(testId) {
            // Get test container and form data
            const testContainer = document.getElementById(`test-${testId}`);
            const form = testContainer.querySelector('.test-form');
            const formData = new FormData(form);
            const testData = Object.fromEntries(formData.entries());
            
            // Get test metadata
            const testTitle = testContainer.querySelector('.test-title').textContent;
            const testCategory = testContainer.querySelector('.test-category').textContent;
            
            // Perform mock validation based on category
            const startTime = performance.now();
            let result;
            
            switch (testCategory) {
                case 'equivalence_partition':
                    result = validateEquivalencePartition(testData);
                    break;
                case 'boundary_value':
                    result = validateBoundaryValue(testData);
                    break;
                case 'error_condition':
                    result = validateErrorCondition(testData);
                    break;
                case 'performance':
                    result = validatePerformance(testData);
                    break;
                case 'security':
                    result = validateSecurity(testData);
                    break;
                default:
                    result = validateGeneral(testData);
            }
            
            const endTime = performance.now();
            const executionTime = endTime - startTime;
            
            return {
                testId: testId,
                testName: testTitle,
                category: testCategory,
                success: result.success,
                result: result.message,
                testData: testData,
                executionTime: Math.round(executionTime * 100) / 100,
                timestamp: new Date().toISOString(),
                details: result.details || {}
            };
        }
        
        // Validation functions for different test categories
        function validateEquivalencePartition(testData) {
            const hasValidInputs = Object.values(testData).some(value => value && value.trim());
            return {
                success: hasValidInputs,
                message: hasValidInputs ? 'Equivalence partition test passed' : 'No valid inputs provided',
                details: { inputCount: Object.keys(testData).length }
            };
        }
        
        function validateBoundaryValue(testData) {
            const numericValues = Object.values(testData).filter(value => !isNaN(value) && value !== '');
            const hasValidBoundaries = numericValues.length >= 2;
            return {
                success: hasValidBoundaries,
                message: hasValidBoundaries ? 'Boundary value test passed' : 'Insufficient boundary values provided',
                details: { boundaryCount: numericValues.length }
            };
        }
        
        function validateErrorCondition(testData) {
            const hasErrorInputs = Object.values(testData).some(value => 
                value === '' || value === 'null' || value === 'undefined' || value.includes('<script>')
            );
            return {
                success: hasErrorInputs,
                message: hasErrorInputs ? 'Error condition test passed' : 'No error conditions triggered',
                details: { errorInputsFound: hasErrorInputs }
            };
        }
        
        function validatePerformance(testData) {
            const iterations = parseInt(testData.iterations) || 1;
            const timeout = parseInt(testData.timeout) || 5000;
            const executionTime = Math.random() * 1000; // Mock execution time
            
            const success = executionTime < timeout;
            return {
                success: success,
                message: success ? `Performance test passed (${executionTime.toFixed(2)}ms)` : 'Performance test failed - timeout exceeded',
                details: { 
                    iterations: iterations,
                    executionTime: executionTime,
                    timeout: timeout
                }
            };
        }
        
        function validateSecurity(testData) {
            const securityThreats = Object.values(testData).filter(value => 
                value.includes('<script>') || 
                value.includes('DROP TABLE') || 
                value.includes('SELECT * FROM') ||
                value.length > 10000
            );
            
            const success = securityThreats.length === 0;
            return {
                success: success,
                message: success ? 'Security test passed - no threats detected' : `Security test failed - ${securityThreats.length} threats detected`,
                details: { threatsDetected: securityThreats.length }
            };
        }
        
        function validateGeneral(testData) {
            const hasInputs = Object.keys(testData).length > 0;
            return {
                success: hasInputs,
                message: hasInputs ? 'General test passed' : 'No test data provided',
                details: { inputFields: Object.keys(testData).length }
            };
        }
        
        function displayTestResult(testId, result) {
            const resultsDiv = document.getElementById(`results-${testId}`);
            const testContainer = document.getElementById(`test-${testId}`);
            
            // Update result display
            resultsDiv.className = `test-results ${result.success ? 'success' : 'failure'}`;
            
            const resultHtml = `
                <h4>Test Results</h4>
                <div class="result-content">
                    <strong>Status:</strong> <span class="status-${result.success ? 'passed' : 'failed'}">
                        ${result.success ? 'PASSED' : 'FAILED'}
                    </span>
                    
                    <strong>Message:</strong> ${result.result}
                    
                    <strong>Execution Time:</strong> ${result.executionTime}ms
                    
                    <strong>Timestamp:</strong> ${new Date(result.timestamp).toLocaleString()}
                    
                    ${result.details ? `<strong>Details:</strong> ${JSON.stringify(result.details, null, 2)}` : ''}
                </div>
            `;
            
            resultsDiv.innerHTML = resultHtml;
            
            // Store result for reporting
            testResults.push(result);
        }
        
        function updateExecutionStats(result) {
            if (result.success) {
                executionStats.passed++;
            } else {
                executionStats.failed++;
            }
            executionStats.total++;
            
            // Update dashboard counters
            updateDashboardCounters();
        }
        
        function updateDashboardCounters() {
            const passedElement = document.getElementById('passed-count');
            const failedElement = document.getElementById('failed-count');
            const skippedElement = document.getElementById('skipped-count');
            
            if (passedElement) passedElement.textContent = executionStats.passed;
            if (failedElement) failedElement.textContent = executionStats.failed;
            if (skippedElement) skippedElement.textContent = executionStats.skipped;
        }
        
        // Utility functions
        function resetTest(testId) {
            const testContainer = document.getElementById(`test-${testId}`);
            const form = testContainer.querySelector('.test-form');
            const resultsDiv = document.getElementById(`results-${testId}`);
            
            form.reset();
            resultsDiv.style.display = 'none';
            testContainer.classList.remove('test-running');
        }
        
        function generateTestData(testId) {
            const testContainer = document.getElementById(`test-${testId}`);
            const category = testContainer.querySelector('.test-category').textContent;
            const inputs = testContainer.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                switch (category) {
                    case 'equivalence_partition':
                        if (input.type === 'number') {
                            input.value = Math.floor(Math.random() * 100);
                        } else {
                            input.value = 'test_value_' + Math.floor(Math.random() * 100);
                        }
                        break;
                    case 'boundary_value':
                        if (input.type === 'number') {
                            input.value = input.name.includes('min') ? 0 : 100;
                        }
                        break;
                    case 'error_condition':
                        if (input.name.includes('null')) {
                            input.value = '';
                        } else if (input.name.includes('invalid')) {
                            input.value = 'invalid_data_type';
                        }
                        break;
                    default:
                        input.value = 'sample_data';
                }
            });
        }
        
        function runAllTests() {
            const allTestForms = document.querySelectorAll('.test-form');
            let testIndex = 0;
            
            const progressCard = document.getElementById('progress-card');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const progressPercentage = document.getElementById('progress-percentage');
            
            progressCard.style.display = 'block';
            
            function runNextTest() {
                if (testIndex >= allTestForms.length) {
                    progressText.textContent = 'All tests completed';
                    setTimeout(() => {
                        progressCard.style.display = 'none';
                        showResults();
                    }, 2000);
                    return;
                }
                
                const form = allTestForms[testIndex];
                const testContainer = form.closest('.test-case-container');
                const testId = testContainer.id.replace('test-', '');
                
                const progress = ((testIndex + 1) / allTestForms.length) * 100;
                progressBar.style.width = progress + '%';
                progressText.textContent = `Running test ${testIndex + 1} of ${allTestForms.length}`;
                progressPercentage.textContent = Math.round(progress) + '%';
                
                executeTest(testId);
                testIndex++;
                
                setTimeout(runNextTest, 2000);
            }
            
            runNextTest();
        }
        
        function runSuiteTests(suiteId) {
            const suite = document.getElementById(`suite-${suiteId}`);
            const testForms = suite.querySelectorAll('.test-form');
            
            testForms.forEach((form, index) => {
                setTimeout(() => {
                    const testContainer = form.closest('.test-case-container');
                    const testId = testContainer.id.replace('test-', '');
                    executeTest(testId);
                }, index * 1500);
            });
        }
        
        function resetSuite(suiteId) {
            const suite = document.getElementById(`suite-${suiteId}`);
            const testContainers = suite.querySelectorAll('.test-case-container');
            
            testContainers.forEach(container => {
                const testId = container.id.replace('test-', '');
                resetTest(testId);
            });
        }
        
        // Chart initialization and updates
        let resultsChart;
        
        function initializeCharts() {
            const ctx = document.getElementById('resultsChart');
            if (ctx) {
                resultsChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Passed', 'Failed', 'Skipped'],
                        datasets: [{
                            data: [0, 0, 0],
                            backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        }
        
        function updateResultsChart() {
            if (resultsChart) {
                resultsChart.data.datasets[0].data = [
                    executionStats.passed,
                    executionStats.failed,
                    executionStats.skipped
                ];
                resultsChart.update();
            }
            
            // Update results table
            updateResultsTable();
        }
        
        function updateResultsTable() {
            const tbody = document.querySelector('#results-table tbody');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            testResults.forEach(result => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${result.testName}</td>
                    <td><span class="badge bg-secondary">${result.category}</span></td>
                    <td><span class="status-${result.success ? 'passed' : 'failed'}">${result.success ? 'PASSED' : 'FAILED'}</span></td>
                    <td>${result.executionTime}ms</td>
                    <td><button class="btn btn-sm btn-outline-info" onclick="showTestDetails('${result.testId}')">View</button></td>
                `;
            });
        }
        
        function showTestDetails(testId) {
            const result = testResults.find(r => r.testId === testId);
            if (result) {
                alert(`Test Details:\n\n${JSON.stringify(result, null, 2)}`);
            }
        }
        
        // Export functions
        function exportResults() {
            const exportData = {
                executionStats: executionStats,
                testResults: testResults,
                timestamp: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `test-results-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function generateReport() {
            // This would generate a comprehensive report
            alert('Report generation feature would be implemented here');
        }
        
        // Update size display for range inputs
        function updateSizeDisplay(testId) {
            const range = document.getElementById(`data-size-${testId}`);
            const display = document.getElementById(`size-display-${testId}`);
            if (range && display) {
                display.textContent = range.value;
            }
        }
"""
