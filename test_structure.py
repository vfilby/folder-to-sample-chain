#!/usr/bin/env python3
"""
Structure Test Runner for NI Sample Chainer

This script runs the project structure validation tests
to ensure the project is properly set up.
"""

import subprocess
import sys
from pathlib import Path

def run_structure_tests():
    """Run the project structure validation tests."""
    print("🏗️  NI Sample Chainer - Structure Validation")
    print("=" * 50)
    
    # Check if we're in the right directory
    project_root = Path.cwd()
    if not (project_root / 'src').exists():
        print("❌ Error: This script must be run from the project root directory")
        print(f"   Current directory: {project_root}")
        print("   Expected to find 'src' directory here")
        sys.exit(1)
    
    print(f"✅ Project root: {project_root}")
    
    # Run structure tests
    test_files = [
        "tests/unit/test_project_structure.py",
        "tests/unit/test_directory_utilities.py", 
        "tests/unit/test_actual_structure.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        test_path = Path(test_file)
        if test_path.exists():
            print(f"\n🧪 Running {test_file}...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ {test_file} passed")
                if result.stdout:
                    print("   Output:", result.stdout.strip())
            except subprocess.CalledProcessError as e:
                print(f"❌ {test_file} failed")
                if e.stdout:
                    print("   STDOUT:", e.stdout.strip())
                if e.stderr:
                    print("   STDERR:", e.stderr.strip())
                all_passed = False
        else:
            print(f"⚠️  Test file {test_file} not found")
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All structure tests passed!")
        print("✅ Project structure is valid")
    else:
        print("⚠️  Some structure tests failed")
        print("   Check the output above for details")
        sys.exit(1)
    
    print("\n💡 Next steps:")
    print("   - Run 'python run_tests.py --type all' for comprehensive testing")
    print("   - Run 'python setup_dev.py' to set up development environment")
    print("   - Check the documentation in AI_RULES.md and PROJECT_SPEC.md")

if __name__ == "__main__":
    run_structure_tests()



