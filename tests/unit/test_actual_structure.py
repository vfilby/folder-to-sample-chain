"""
Actual Project Structure Tests for NI Sample Chainer

These tests validate the actual project structure based on the
real directory layout and file presence.
"""

import pytest
import os
import sys
from pathlib import Path
from typing import List, Set, Dict

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

class TestActualProjectStructure:
    """Test the actual project structure based on real filesystem."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        
        # Expected structure based on the actual project setup
        self.expected_structure = {
            'directories': {
                'src',
                'src/audio_processing',
                'src/digitakt_export',
                'src/utils',
                'tests',
                'tests/unit',
                'tests/integration',
                'tests/utils',
                'docs',
                'examples',
                'output_samples'
            },
            'python_files': {
                'src/__init__.py',
                'src/main.py',
                'src/audio_processing/__init__.py',
                'src/digitakt_export/__init__.py',
                'src/utils/__init__.py',
                'tests/__init__.py',
                'tests/unit/__init__.py',
                'tests/unit/test_basic_functionality.py',
                'tests/unit/test_project_structure.py',
                'tests/unit/test_directory_utilities.py',
                'tests/unit/test_actual_structure.py',
                'tests/integration/__init__.py',
                'tests/utils/__init__.py',
                'tests/utils/test_data_generator.py',
                'examples/basic_usage.py',
                'setup_dev.py',
                'run_tests.py'
            },
            'markdown_files': {
                'README.md',
                'AI_RULES.md',
                'PROJECT_SPEC.md',
                'DEVELOPMENT_ROADMAP.md'
            },
            'config_files': {
                'config.yaml',
                'requirements.txt',
                'pytest.ini'
            },
            'other_files': {
                '.gitignore'
            }
        }
    
    def test_project_root_exists(self):
        """Test that the project root directory exists."""
        assert self.project_root.exists(), f"Project root {self.project_root} does not exist"
        assert self.project_root.is_dir(), f"Project root {self.project_root} is not a directory"
    
    def test_expected_directories_exist(self):
        """Test that all expected directories exist."""
        missing_dirs = []
        for expected_dir in self.expected_structure['directories']:
            dir_path = self.project_root / expected_dir
            if not dir_path.exists():
                missing_dirs.append(expected_dir)
            elif not dir_path.is_dir():
                missing_dirs.append(f"{expected_dir} (exists but is not a directory)")
        
        assert not missing_dirs, f"Missing or invalid directories: {missing_dirs}"
    
    def test_expected_python_files_exist(self):
        """Test that all expected Python files exist."""
        missing_files = []
        for expected_file in self.expected_structure['python_files']:
            file_path = self.project_root / expected_file
            if not file_path.exists():
                missing_files.append(expected_file)
            elif not file_path.is_file():
                missing_files.append(f"{expected_file} (exists but is not a file)")
            elif not file_path.suffix == '.py':
                missing_files.append(f"{expected_file} (exists but is not a Python file)")
        
        assert not missing_files, f"Missing or invalid Python files: {missing_files}"
    
    def test_expected_markdown_files_exist(self):
        """Test that all expected markdown files exist."""
        missing_files = []
        for expected_file in self.expected_structure['markdown_files']:
            file_path = self.project_root / expected_file
            if not file_path.exists():
                missing_files.append(expected_file)
            elif not file_path.is_file():
                missing_files.append(f"{expected_file} (exists but is not a file)")
            elif not file_path.suffix == '.md':
                missing_files.append(f"{expected_file} (exists but is not a markdown file)")
        
        assert not missing_files, f"Missing or invalid markdown files: {missing_files}"
    
    def test_expected_config_files_exist(self):
        """Test that all expected configuration files exist."""
        missing_files = []
        for expected_file in self.expected_structure['config_files']:
            file_path = self.project_root / expected_file
            if not file_path.exists():
                missing_files.append(expected_file)
            elif not file_path.is_file():
                missing_files.append(f"{expected_file} (exists but is not a file)")
        
        assert not missing_files, f"Missing or invalid config files: {missing_files}"
    
    def test_expected_other_files_exist(self):
        """Test that all expected other files exist."""
        missing_files = []
        for expected_file in self.expected_structure['other_files']:
            file_path = self.project_root / expected_file
            if not file_path.exists():
                missing_files.append(expected_file)
            elif not file_path.is_file():
                missing_files.append(f"{expected_file} (exists but is not a file)")
        
        assert not missing_files, f"Missing or invalid other files: {missing_files}"
    
    def test_python_package_structure(self):
        """Test that Python packages are properly structured."""
        python_packages = [
            'src',
            'src/audio_processing',
            'src/digitakt_export',
            'src/utils',
            'tests',
            'tests/unit',
            'tests/integration',
            'tests/utils'
        ]
        
        for package in python_packages:
            init_file = self.project_root / package / '__init__.py'
            assert init_file.exists(), f"Missing __init__.py in package {package}"
            assert init_file.is_file(), f"__init__.py in {package} is not a file"
    
    def test_source_code_organization(self):
        """Test that source code is properly organized."""
        src_dir = self.project_root / 'src'
        
        # Check main entry point
        main_file = src_dir / 'main.py'
        assert main_file.exists(), "Missing main.py entry point"
        
        # Check module structure
        modules = ['audio_processing', 'digitakt_export', 'utils']
        for module in modules:
            module_dir = src_dir / module
            module_init = module_dir / '__init__.py'
            assert module_dir.exists(), f"Missing module directory: {module}"
            assert module_init.exists(), f"Missing __init__.py in module: {module}"
    
    def test_test_structure(self):
        """Test that the test suite is properly organized."""
        tests_dir = self.project_root / 'tests'
        
        # Check test categories
        test_categories = ['unit', 'integration', 'utils']
        for category in test_categories:
            category_dir = tests_dir / category
            assert category_dir.exists(), f"Missing test category: {category}"
            assert category_dir.is_dir(), f"Test category {category} is not a directory"
        
        # Check that we have test files
        test_files = list(tests_dir.rglob('test_*.py'))
        assert len(test_files) > 0, "No test files found"
        
        # Check that test files follow naming convention
        for test_file in test_files:
            assert test_file.name.startswith('test_'), f"Test file {test_file.name} doesn't follow naming convention"
    
    def test_documentation_structure(self):
        """Test that documentation is properly organized."""
        docs_dir = self.project_root / 'docs'
        assert docs_dir.exists(), "Missing docs directory"
        
        # Check for key documentation files
        key_docs = ['README.md', 'AI_RULES.md', 'PROJECT_SPEC.md', 'DEVELOPMENT_ROADMAP.md']
        for doc in key_docs:
            doc_file = self.project_root / doc
            assert doc_file.exists(), f"Missing key documentation: {doc}"
    
    def test_examples_structure(self):
        """Test that examples are properly organized."""
        examples_dir = self.project_root / 'examples'
        assert examples_dir.exists(), "Missing examples directory"
        
        # Check for basic usage example
        basic_usage = examples_dir / 'basic_usage.py'
        assert basic_usage.exists(), "Missing basic_usage.py example"
    
    def test_output_directory_structure(self):
        """Test that output directories are properly set up."""
        output_dir = self.project_root / 'output_samples'
        assert output_dir.exists(), "Missing output_samples directory"
        assert output_dir.is_dir(), "output_samples is not a directory"
    
    def test_git_ignore_present(self):
        """Test that .gitignore is present and properly configured."""
        gitignore = self.project_root / '.gitignore'
        assert gitignore.exists(), "Missing .gitignore file"
        
        # Check for key ignore patterns
        with open(gitignore, 'r') as f:
            content = f.read()
            key_patterns = ['__pycache__', '*.py[cod]', '.pytest_cache']
            for pattern in key_patterns:
                assert pattern in content, f"Missing gitignore pattern: {pattern}"
    
    def test_pytest_configuration(self):
        """Test that pytest configuration is present."""
        pytest_config = self.project_root / 'pytest.ini'
        assert pytest_config.exists(), "Missing pytest.ini configuration file"
        assert pytest_config.is_file(), "pytest.ini is not a file"
    
    def test_requirements_file_format(self):
        """Test that requirements.txt has proper format."""
        requirements_file = self.project_root / 'requirements.txt'
        assert requirements_file.exists(), "requirements.txt not found"
        
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
            
        # Check that file is not empty
        assert len(lines) > 0, "requirements.txt is empty"
        
        # Check that lines are properly formatted (basic validation)
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # Should contain package name and version
                assert '>=' in line or '==' in line or '~=' in line, \
                    f"Line {i} in requirements.txt doesn't specify version: {line}"
    
    def test_config_yaml_format(self):
        """Test that config.yaml has proper YAML format."""
        config_file = self.project_root / 'config.yaml'
        assert config_file.exists(), "config.yaml not found"
        
        try:
            import yaml
            with open(config_file, 'r') as f:
                yaml.safe_load(f)
        except ImportError:
            pytest.skip("PyYAML not available for testing")
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in config.yaml: {e}")
    
    def test_markdown_files_are_readable(self):
        """Test that markdown files are readable and not empty."""
        markdown_files = list(self.project_root.rglob('*.md'))
        
        for md_file in markdown_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content.strip()) > 0, f"Markdown file {md_file} is empty"
                assert len(content) > 100, f"Markdown file {md_file} seems too short"
    
    def test_python_files_are_valid(self):
        """Test that Python files can be imported without syntax errors."""
        python_files = list(self.project_root.rglob('*.py'))
        
        for py_file in python_files:
            try:
                # Try to compile the Python file
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                pytest.fail(f"Error reading {py_file}: {e}")

class TestFileCounts:
    """Test that we have the expected number of files in each category."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_python_file_count(self):
        """Test that we have the expected number of Python files."""
        python_files = list(self.project_root.rglob('*.py'))
        
        # We should have at least the core files
        expected_min_count = 18  # Adjust based on actual project
        assert len(python_files) >= expected_min_count, \
            f"Expected at least {expected_min_count} Python files, found {len(python_files)}"
        
        print(f"📊 Found {len(python_files)} Python files")
    
    def test_markdown_file_count(self):
        """Test that we have the expected number of markdown files."""
        markdown_files = list(self.project_root.rglob('*.md'))
        
        # We should have the key documentation files
        expected_count = 4  # README, AI_RULES, PROJECT_SPEC, DEVELOPMENT_ROADMAP
        assert len(markdown_files) >= expected_count, \
            f"Expected at least {expected_count} markdown files, found {len(markdown_files)}"
        
        print(f"📊 Found {len(markdown_files)} markdown files")
    
    def test_test_file_count(self):
        """Test that we have the expected number of test files."""
        test_files = list(self.project_root.rglob('test_*.py'))
        
        # We should have several test files
        expected_min_count = 4  # Adjust based on actual project
        assert len(test_files) >= expected_min_count, \
            f"Expected at least {expected_min_count} test files, found {len(test_files)}"
        
        print(f"📊 Found {len(test_files)} test files")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
