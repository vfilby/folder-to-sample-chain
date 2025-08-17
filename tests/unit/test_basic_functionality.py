"""
Basic functionality tests for NI Sample Chainer

These tests verify the basic structure and functionality
of the audio processing tool.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from main import process_audio_directory

class TestBasicFunctionality:
    """Test basic functionality of the NI Sample Chainer."""
    
    def test_process_audio_directory_import(self):
        """Test that the function can be imported and has correct signature."""
        # Check that function exists and has correct parameters
        import inspect
        sig = inspect.signature(process_audio_directory)
        params = list(sig.parameters.keys())
        
        # Should have these parameters: input_dir, output_dir, dry_run
        expected_params = ['input_dir', 'output_dir', 'dry_run']
        for param in expected_params:
            assert param in params, f"Missing parameter: {param}"
        
        # Should not have removed parameters
        removed_params = ['sample_duration', 'overlap', 'crossfade', 'quality', 'parallel_processes']
        for param in removed_params:
            assert param not in params, f"Removed parameter still present: {param}"
        
        print("✅ Function signature is correct")
    
    def test_process_audio_directory_dry_run(self):
        """Test that dry run mode works correctly."""
        # Create a temporary test directory
        test_input = Path("tests/audio_samples")
        test_output = Path("test_output")
        
        if test_input.exists():
            result = process_audio_directory(
                input_dir=str(test_input),
                output_dir=str(test_output),
                dry_run=True
            )
            
            # Check that result has expected structure
            assert isinstance(result, dict)
            assert 'status' in result
            assert result['status'] == 'dry_run'
            print("✅ Dry run mode works correctly")
        else:
            pytest.skip("Test audio samples directory not found")
    
    def test_process_audio_directory_defaults(self):
        """Test that default parameters work correctly."""
        # Test that function can be called with minimal parameters
        test_input = Path("tests/audio_samples")
        test_output = Path("test_output")
        
        if test_input.exists():
            result = process_audio_directory(
                input_dir=str(test_input),
                output_dir=str(test_output)
            )
            
            # Should return dry run result since no actual processing
            assert isinstance(result, dict)
            assert 'status' in result
            print("✅ Default parameters work correctly")
        else:
            pytest.skip("Test audio samples directory not found")

if __name__ == "__main__":
    pytest.main([__file__])



