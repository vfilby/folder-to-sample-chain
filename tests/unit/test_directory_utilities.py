"""
Directory Utility Tests for NI Sample Chainer

These tests validate utility functions for directory operations,
file discovery, and path management.
"""

import pytest
import os
import sys
from pathlib import Path
from typing import List, Set, Dict

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

class TestDirectoryDiscovery:
    """Test directory discovery and traversal utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dirs = [
            'src',
            'src/audio_processing',
            'src/digitakt_export',
            'src/utils',
            'tests',
            'tests/unit',
            'tests/integration',
            'docs',
            'examples',
            'output_samples'
        ]
    
    def test_find_all_directories(self):
        """Test finding all directories in the project."""
        all_dirs = []
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                all_dirs.append(str(dir_path.relative_to(self.project_root)))
        
        # Check that expected directories are found
        for expected_dir in self.test_dirs:
            assert expected_dir in all_dirs, f"Expected directory {expected_dir} not found"
        
        # Check that we have a reasonable number of directories
        assert len(all_dirs) >= len(self.test_dirs), f"Expected at least {len(self.test_dirs)} directories, found {len(all_dirs)}"
    
    def test_find_python_files(self):
        """Test finding all Python files in the project."""
        python_files = list(self.project_root.rglob('*.py'))
        
        # Check that we have Python files
        assert len(python_files) > 0, "No Python files found"
        
        # Check that expected Python files exist
        expected_py_files = [
            'src/main.py',
            'src/__init__.py',
            'src/audio_processing/__init__.py',
            'src/digitakt_export/__init__.py',
            'src/utils/__init__.py',
            'tests/unit/test_basic_functionality.py',
            'tests/unit/test_project_structure.py',
            'tests/unit/test_directory_utilities.py',
            'examples/basic_usage.py',
            'setup_dev.py'
        ]
        
        for expected_file in expected_py_files:
            file_path = self.project_root / expected_file
            assert file_path in python_files, f"Expected Python file {expected_file} not found"
    
    def test_find_markdown_files(self):
        """Test finding all markdown files in the project."""
        markdown_files = list(self.project_root.rglob('*.md'))
        
        # Check that we have markdown files
        assert len(markdown_files) > 0, "No markdown files found"
        
        # Check that expected markdown files exist
        expected_md_files = [
            'README.md',
            'AI_RULES.md',
            'PROJECT_SPEC.md',
            'DEVELOPMENT_ROADMAP.md'
        ]
        
        for expected_file in expected_md_files:
            file_path = self.project_root / expected_file
            assert file_path in markdown_files, f"Expected markdown file {expected_file} not found"
    
    def test_find_config_files(self):
        """Test finding configuration files in the project."""
        config_extensions = ['.yaml', '.yml', '.txt', '.cfg', '.ini']
        config_files = []
        
        for ext in config_extensions:
            config_files.extend(self.project_root.rglob(f'*{ext}'))
        
        # Check that we have configuration files
        assert len(config_files) > 0, "No configuration files found"
        
        # Check that expected config files exist
        expected_config_files = [
            'config.yaml',
            'requirements.txt'
        ]
        
        for expected_file in expected_config_files:
            file_path = self.project_root / expected_file
            assert any(str(file_path) == str(cf) for cf in config_files), \
                f"Expected config file {expected_file} not found"

class TestPathValidation:
    """Test path validation and manipulation utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_path_components(self):
        """Test path component extraction and manipulation."""
        test_path = self.project_root / 'src' / 'audio_processing' / 'wav_handler.py'
        
        # Test path components
        assert test_path.parts[-1] == 'wav_handler.py', "Filename not extracted correctly"
        assert test_path.stem == 'wav_handler', "Stem not extracted correctly"
        assert test_path.suffix == '.py', "Extension not extracted correctly"
        assert test_path.parent.name == 'audio_processing', "Parent directory name not extracted correctly"
    
    def test_relative_paths(self):
        """Test relative path calculations."""
        src_dir = self.project_root / 'src'
        test_file = self.project_root / 'tests' / 'unit' / 'test_basic_functionality.py'
        
        # Calculate relative path from project root to test file
        relative_path = test_file.relative_to(self.project_root)
        expected_relative = Path('tests') / 'unit' / 'test_basic_functionality.py'
        assert relative_path == expected_relative, f"Relative path calculation failed: {relative_path} != {expected_relative}"
        
        # Test relative path from tests to src (using parent directory)
        tests_dir = self.project_root / 'tests'
        parent_dir = tests_dir.parent
        src_relative = src_dir.relative_to(parent_dir)
        expected_src_relative = Path('src')
        assert src_relative == expected_src_relative, f"Source relative path failed: {src_relative} != {expected_src_relative}"
    
    def test_path_existence_checks(self):
        """Test various path existence and type checks."""
        src_dir = self.project_root / 'src'
        main_file = src_dir / 'main.py'
        non_existent = src_dir / 'non_existent.py'
        
        # Test existence checks
        assert src_dir.exists(), "src directory should exist"
        assert src_dir.is_dir(), "src should be a directory"
        assert main_file.exists(), "main.py should exist"
        assert main_file.is_file(), "main.py should be a file"
        assert not non_existent.exists(), "non_existent.py should not exist"
    
    def test_path_resolution(self):
        """Test path resolution and absolute path handling."""
        # Test resolving relative paths
        relative_path = Path('src') / 'main.py'
        absolute_path = (self.project_root / relative_path).resolve()
        
        assert absolute_path.is_absolute(), "Resolved path should be absolute"
        assert absolute_path.exists(), "Resolved path should exist"
        assert absolute_path.samefile(self.project_root / 'src' / 'main.py'), "Path resolution failed"

class TestFileOperations:
    """Test file operation utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dir = self.project_root / 'temp_test'
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_directory_creation(self):
        """Test directory creation utilities."""
        # Create test directory
        self.test_dir.mkdir(exist_ok=True)
        assert self.test_dir.exists(), "Test directory should be created"
        assert self.test_dir.is_dir(), "Test directory should be a directory"
        
        # Create nested directories
        nested_dir = self.test_dir / 'nested' / 'deeply'
        nested_dir.mkdir(parents=True, exist_ok=True)
        assert nested_dir.exists(), "Nested directories should be created"
    
    def test_file_operations(self):
        """Test basic file operations."""
        # Ensure test directory exists
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test file
        test_file = self.test_dir / 'test.txt'
        test_content = "This is a test file\nWith multiple lines\n"
        
        # Write file
        test_file.write_text(test_content)
        assert test_file.exists(), "Test file should be created"
        assert test_file.is_file(), "Test file should be a file"
        
        # Read file
        read_content = test_file.read_text()
        assert read_content == test_content, "File content should match what was written"
        
        # Check file size
        assert test_file.stat().st_size == len(test_content), "File size should match content length"
    
    def test_file_patterns(self):
        """Test file pattern matching and filtering."""
        # Create test files with different extensions
        test_files = [
            'test1.py',
            'test2.py',
            'data.txt',
            'config.yaml',
            'README.md'
        ]
        
        self.test_dir.mkdir(exist_ok=True)
        for filename in test_files:
            (self.test_dir / filename).touch()
        
        # Test pattern matching
        py_files = list(self.test_dir.glob('*.py'))
        assert len(py_files) == 2, f"Expected 2 Python files, found {len(py_files)}"
        
        txt_files = list(self.test_dir.glob('*.txt'))
        assert len(txt_files) == 1, f"Expected 1 text file, found {len(txt_files)}"
        
        md_files = list(self.test_dir.glob('*.md'))
        assert len(md_files) == 1, f"Expected 1 markdown file, found {len(md_files)}"

class TestProjectStructureValidation:
    """Test project structure validation utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_validate_project_structure(self):
        """Test comprehensive project structure validation."""
        # Define expected structure
        expected_structure = {
            'directories': {
                'src',
                'src/audio_processing',
                'src/digitakt_export',
                'src/utils',
                'tests',
                'tests/unit',
                'tests/integration',
                'docs',
                'examples',
                'output_samples'
            },
            'files': {
                'src/main.py',
                'src/__init__.py',
                'README.md',
                'requirements.txt',
                'config.yaml'
            }
        }
        
        # Validate directories
        for expected_dir in expected_structure['directories']:
            dir_path = self.project_root / expected_dir
            assert dir_path.exists(), f"Expected directory {expected_dir} not found"
            assert dir_path.is_dir(), f"{expected_dir} exists but is not a directory"
        
        # Validate files
        for expected_file in expected_structure['files']:
            file_path = self.project_root / expected_file
            assert file_path.exists(), f"Expected file {expected_file} not found"
            assert file_path.is_file(), f"{expected_file} exists but is not a file"
    
    def test_python_package_validation(self):
        """Test Python package structure validation."""
        python_packages = [
            'src',
            'src/audio_processing',
            'src/digitakt_export',
            'src/utils',
            'tests',
            'tests/unit',
            'tests/integration'
        ]
        
        for package in python_packages:
            package_path = self.project_root / package
            init_file = package_path / '__init__.py'
            
            assert package_path.exists(), f"Package directory {package} not found"
            assert package_path.is_dir(), f"{package} exists but is not a directory"
            assert init_file.exists(), f"Missing __init__.py in package {package}"
            assert init_file.is_file(), f"__init__.py in {package} is not a file"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
