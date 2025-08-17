# Testing Guide for NI Sample Chainer

This guide explains how to run tests and validate the project structure for the NI Sample Chainer project.

## 🧪 Test Structure Overview

The project includes a comprehensive test suite organized as follows:

```
tests/
├── unit/                           # Unit tests for individual functions
│   ├── test_basic_functionality.py    # Basic functionality tests
│   ├── test_project_structure.py      # Project structure validation
│   ├── test_directory_utilities.py    # Directory utility tests
│   └── test_actual_structure.py       # Actual filesystem structure tests
├── integration/                    # Integration tests for complete workflows
├── utils/                         # Test utilities and helpers
│   └── test_data_generator.py         # Test data generation utilities
└── fixtures/                      # Test data and configurations
```

## 🚀 Quick Start Testing

### 1. Run Structure Validation (Recommended First Step)

Validate that the project structure is correct:

```bash
python test_structure.py
```

This will run the core structure validation tests to ensure everything is set up correctly.

### 2. Run All Tests

Run the complete test suite:

```bash
python run_tests.py --type all
```

### 3. Run Specific Test Categories

```bash
# Run only unit tests
python run_tests.py --type unit

# Run only integration tests  
python run_tests.py --type integration

# Run only structure tests
python run_tests.py --type structure

# Run only basic functionality tests
python run_tests.py --type basic
```

### 4. Run Tests with Coverage

Generate coverage reports:

```bash
python run_tests.py --type all --coverage
```

## 🔧 Individual Test Files

### Structure Validation Tests

#### `test_project_structure.py`
- Validates expected directories and files exist
- Checks Python package structure
- Verifies documentation organization
- Tests configuration file presence

#### `test_directory_utilities.py`
- Tests directory discovery and traversal
- Validates path manipulation utilities
- Tests file operation functions
- Tests project structure validation utilities

#### `test_actual_structure.py`
- Tests the actual project structure based on real filesystem
- Validates file counts and organization
- Tests Python file syntax
- Verifies configuration file formats

### Basic Functionality Tests

#### `test_basic_functionality.py`
- Tests the main application functions
- Validates parameter handling
- Tests default configurations
- Tests basic CLI functionality

### Test Utilities

#### `test_data_generator.py`
- Generates mock audio files for testing
- Creates test configurations
- Sets up test output structures
- Provides temporary workspaces for testing

## 📊 Test Configuration

### pytest.ini
The project includes a `pytest.ini` configuration file with:

- Test discovery patterns
- Output formatting options
- Markers for different test types
- Coverage configuration options
- Warning filters

### Test Markers
Tests are organized with markers for easy filtering:

- `unit`: Unit tests for individual functions
- `integration`: Integration tests for complete workflows
- `slow`: Tests that take longer to run
- `audio`: Tests that require audio files
- `structure`: Tests for project structure validation

## 🎯 Running Tests with pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_project_structure.py -v

# Run tests with specific markers
pytest tests/ -m unit -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run tests and stop on first failure
pytest tests/ -x

# Run tests in parallel (if pytest-xdist is installed)
pytest tests/ -n auto
```

## 🔍 Test Data Generation

### Creating Test Data

The test data generator creates mock files and configurations:

```python
from tests.utils.test_data_generator import TestDataGenerator

# Create test data generator
generator = TestDataGenerator()

# Create mock audio files
audio_dir = generator.create_test_audio_directory(5)

# Create test configurations
config_file = generator.create_test_config('test_config.yaml')

# Create test output structure
output_dir = generator.create_test_output_structure()

# Create temporary workspace
workspace = generator.create_temp_workspace()

# Clean up when done
generator.cleanup_temp_files()
```

### Test Data Structure

```
tests/fixtures/
├── audio/                    # Mock audio files
├── configs/                  # Test configuration files
├── outputs/                  # Test output structures
└── temp/                     # Temporary test workspaces
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
If you get import errors, ensure you're running tests from the project root:

```bash
cd /path/to/ni-sample-chainer
python test_structure.py
```

#### 2. Missing Dependencies
Install required testing dependencies:

```bash
pip install pytest pytest-cov pyyaml
```

#### 3. Test Discovery Issues
Check that test files follow naming conventions:
- Test files must start with `test_`
- Test classes must start with `Test`
- Test methods must start with `test_`

#### 4. Permission Issues
Ensure test directories are writable:

```bash
chmod -R 755 tests/
```

### Debug Mode

Run tests with verbose output for debugging:

```bash
pytest tests/ -v -s --tb=long
```

## 📈 Coverage Reports

### HTML Coverage Report

Generate detailed HTML coverage reports:

```bash
pytest tests/ --cov=src --cov-report=html
```

Open `htmlcov/index.html` in your browser to view coverage details.

### Terminal Coverage Report

View coverage in the terminal:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Coverage Configuration

Coverage settings can be configured in `pytest.ini`:

```ini
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python run_tests.py --type all --coverage
```

## 📋 Test Checklist

Before committing code, ensure:

- [ ] All tests pass: `python run_tests.py --type all`
- [ ] Structure validation passes: `python test_structure.py`
- [ ] Coverage is adequate: `python run_tests.py --type all --coverage`
- [ ] New functionality has corresponding tests
- [ ] Test data is properly cleaned up
- [ ] Documentation is updated if needed

## 🎉 Success Indicators

Your testing setup is working correctly when:

✅ `python test_structure.py` runs without errors  
✅ `python run_tests.py --type all` completes successfully  
✅ Coverage reports are generated  
✅ All expected directories and files are validated  
✅ Python files compile without syntax errors  
✅ Configuration files are properly formatted  

## 💡 Best Practices

1. **Run structure tests first** to ensure project setup is correct
2. **Use the test runner scripts** for consistent test execution
3. **Generate coverage reports** to identify untested code
4. **Clean up test data** to avoid accumulation of temporary files
5. **Write tests for new functionality** as you develop
6. **Use descriptive test names** that explain what is being tested
7. **Group related tests** in test classes for better organization

## 🔗 Related Documentation

- [AI_RULES.md](AI_RULES.md) - Development guidelines and standards
- [PROJECT_SPEC.md](PROJECT_SPEC.md) - Project requirements and specifications
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) - Development phases and milestones
- [README.md](README.md) - Project overview and usage

---

**Happy Testing! 🧪✨**



