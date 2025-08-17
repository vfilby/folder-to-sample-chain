#!/usr/bin/env python3
"""
Test Runner for NI Sample Chainer

This script provides an easy way to run different types of tests
and provides useful output for development.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(command, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ {description} completed successfully")
            return result.stdout, result.stderr, True
        else:
            result = subprocess.run(command, shell=True, check=True)
            print(f"✅ {description} completed successfully")
            return "", "", True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")
        return e.stdout, e.stderr, False

def check_dependencies():
    """Check if required testing dependencies are installed."""
    print("🔍 Checking testing dependencies...")
    
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} is available")
    except ImportError:
        print("❌ pytest is not installed")
        print("   Install with: pip install pytest")
        return False
    
    try:
        import yaml
        print("✅ PyYAML is available")
    except ImportError:
        print("⚠️  PyYAML is not installed (some tests may be skipped)")
    
    return True

def run_structure_tests():
    """Run project structure validation tests."""
    print("\n🏗️  Running project structure tests...")
    
    structure_tests = [
        "tests/unit/test_project_structure.py",
        "tests/unit/test_directory_utilities.py"
    ]
    
    for test_file in structure_tests:
        if Path(test_file).exists():
            stdout, stderr, success = run_command(
                f"python -m pytest {test_file} -v --tb=short",
                f"Running {test_file}"
            )
            if not success:
                print(f"⚠️  Structure test {test_file} had issues")
        else:
            print(f"⚠️  Test file {test_file} not found")

def run_basic_tests():
    """Run basic functionality tests."""
    print("\n🧪 Running basic functionality tests...")
    
    stdout, stderr, success = run_command(
        "python -m pytest tests/unit/test_basic_functionality.py -v --tb=short",
        "Running basic functionality tests"
    )
    
    if not success:
        print("⚠️  Basic functionality tests had issues")

def run_all_tests():
    """Run all available tests."""
    print("\n🚀 Running all tests...")
    
    stdout, stderr, success = run_command(
        "python -m pytest tests/ -v --tb=short",
        "Running all tests"
    )
    
    if not success:
        print("⚠️  Some tests failed")
        return False
    
    return True

def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("\n📊 Running tests with coverage...")
    
    try:
        import pytest_cov
        stdout, stderr, success = run_command(
            "python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing",
            "Running tests with coverage"
        )
        
        if success:
            print("📁 Coverage report generated in htmlcov/ directory")
        
        return success
    except ImportError:
        print("❌ pytest-cov not installed")
        print("   Install with: pip install pytest-cov")
        return False

def run_specific_test_category(category):
    """Run tests from a specific category."""
    print(f"\n🎯 Running {category} tests...")
    
    if category == "unit":
        stdout, stderr, success = run_command(
            "python -m pytest tests/unit/ -v --tb=short",
            f"Running {category} tests"
        )
    elif category == "integration":
        stdout, stderr, success = run_command(
            "python -m pytest tests/integration/ -v --tb=short",
            f"Running {category} tests"
        )
    elif category == "structure":
        run_structure_tests()
        return True
    else:
        print(f"❌ Unknown test category: {category}")
        return False
    
    return success

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Test Runner for NI Sample Chainer")
    parser.add_argument(
        "--type", "-t",
        choices=["all", "unit", "integration", "structure", "basic"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check testing dependencies"
    )
    
    args = parser.parse_args()
    
    print("🎵 NI Sample Chainer - Test Runner")
    print("=" * 50)
    
    # Check dependencies if requested
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        return
    
    # Check dependencies before running tests
    if not check_dependencies():
        print("❌ Cannot run tests without required dependencies")
        sys.exit(1)
    
    # Run tests based on type
    success = True
    
    if args.type == "all":
        if args.coverage:
            success = run_tests_with_coverage()
        else:
            success = run_all_tests()
    elif args.type == "basic":
        run_basic_tests()
    elif args.type == "structure":
        run_structure_tests()
    else:
        success = run_specific_test_category(args.type)
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test run completed successfully!")
    else:
        print("⚠️  Test run completed with some issues")
        print("   Check the output above for details")
    
    print("\n💡 Tips:")
    print("   - Use --coverage to generate coverage reports")
    print("   - Use --type structure to validate project structure")
    print("   - Use --check-deps to verify dependencies")
    print("   - Check pytest.ini for configuration options")

if __name__ == "__main__":
    main()



