#!/usr/bin/env python3
"""Backward-compatible entry point for the test generator.

This script delegates execution to the package's command-line interface so
existing workflows that invoke ``python main.py`` continue to function.
"""

from qe_test_case_generator.cli import cli


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
