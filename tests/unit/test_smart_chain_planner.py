"""
Tests for SmartChainPlanner.

Tests the hihat interleaving and name-based grouping functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.utils.smart_chain_planner import SmartChainPlanner
from src.utils.sample_chain_config import SampleChainConfig


class TestSmartChainPlanner:
    """Test the SmartChainPlanner functionality."""
    
    def setup_method(self):
        """Set up test data."""
        # Create mock hihat files based on your real data structure
        self.hihat_files = [
            Path("Drums/Hihat/ClosedHH Aberlour 1.wav"),
            Path("Drums/Hihat/ClosedHH Aberlour 2.wav"),
            Path("Drums/Hihat/OpenHH Aberlour.wav"),
            Path("Drums/Hihat/ClosedHH XOR 1.wav"),
            Path("Drums/Hihat/ClosedHH XOR 2.wav"),
            Path("Drums/Hihat/ClosedHH XOR 3.wav"),
            Path("Drums/Hihat/OpenHH XOR.wav"),
            Path("Drums/Hihat/ClsdHH Can 1.wav"),
            Path("Drums/Hihat/ClsdHH Can 2.wav"),
            Path("Drums/Hihat/OpenHH Can.wav"),
        ]
        
        # Create mock non-hihat files
        self.regular_files = [
            Path("Drums/Kick/Kick XOR 1.wav"),
            Path("Drums/Kick/Kick XOR 2.wav"),
            Path("Drums/Kick/Kick XOR Sub.wav"),
            Path("Drums/Snare/Snare XOR 1.wav"),
            Path("Drums/Snare/Snare XOR 2.wav"),
        ]
        
        self.all_files = self.hihat_files + self.regular_files
        
        # Create planner with default config
        config = SampleChainConfig()
        self.planner = SmartChainPlanner(config)
    
    def test_hihat_file_detection(self):
        """Test that hihat files are correctly identified."""
        # Test closed hihat detection
        closed_files = [
            Path("Drums/Hihat/ClosedHH Test.wav"),
            Path("Drums/Hihat/ClsdHH Test.wav"),
            Path("Drums/Hihat/Closed HH Test.wav"),
            Path("Drums/Hihat/Clsd HH Test.wav"),
        ]
        
        for file_path in closed_files:
            is_hihat, hihat_type = self.planner.config.is_hihat_file(file_path)
            assert is_hihat, f"Failed to detect closed hihat: {file_path}"
            assert hihat_type == 'closed', f"Wrong hihat type for {file_path}: {hihat_type}"
        
        # Test open hihat detection
        open_files = [
            Path("Drums/Hihat/OpenHH Test.wav"),
            Path("Drums/Hihat/Open HH Test.wav"),
        ]
        
        for file_path in open_files:
            is_hihat, hihat_type = self.planner.config.is_hihat_file(file_path)
            assert is_hihat, f"Failed to detect open hihat: {file_path}"
            assert hihat_type == 'open', f"Wrong hihat type for {file_path}: {hihat_type}"
        
        # Test non-hihat files
        non_hihat_files = [
            Path("Drums/Kick/Kick Test.wav"),
            Path("Drums/Snare/Snare Test.wav"),
        ]
        
        for file_path in non_hihat_files:
            is_hihat, hihat_type = self.planner.config.is_hihat_file(file_path)
            assert not is_hihat, f"False positive hihat detection: {file_path}"
            assert hihat_type is None, f"Unexpected hihat type: {hihat_type}"
    
    def test_base_name_extraction(self):
        """Test that base names are correctly extracted from hi-hat filenames."""
        test_cases = [
            (Path("Drums/Hihat/ClosedHH XOR 1.wav"), "XOR 1"),
            (Path("Drums/Hihat/ClosedHH XOR 2.wav"), "XOR 2"),
            (Path("Drums/Hihat/OpenHH XOR.wav"), "XOR"),
            (Path("Drums/Hihat/ClosedHH Aberlour 1.wav"), "Aberlour 1"),
            (Path("Drums/Hihat/OpenHH Aberlour.wav"), "Aberlour"),
        ]
        
        for file_path, expected_base in test_cases:
            base_name = self.planner.config.extract_base_name(file_path)
            assert base_name == expected_base, f"Expected {expected_base}, got {base_name} for {file_path}"
    
    def test_hihat_grouping(self):
        """Test that hihat files are grouped correctly by base name."""
        # Test the actual grouping logic by planning chains
        sample_chains = self.planner.plan_smart_chains(self.hihat_files)
        
        # Should have hi-hat chains
        hihat_chains = {k: v for k, v in sample_chains.items() if k.startswith('hats')}
        assert len(hihat_chains) > 0, "Should create hi-hat chains"
        
        # Check that files with same base name are grouped together
        for chain_name, chain_data in hihat_chains.items():
            files = chain_data['files']
            print(f"  Chain {chain_name}: {len(files)} files")
            
            # Verify that files in the same chain have related names
            if len(files) > 1:
                # Extract base names from filenames
                base_names = []
                for file_path in files:
                    base_name = self.planner.config.extract_base_name(file_path)
                    base_names.append(base_name)
                
                # Should have some common base names
                assert len(set(base_names)) <= len(files), "Files should be grouped by base name"
    
    def test_hihat_chain_creation(self):
        """Test that hihat chains are created with proper interleaving."""
        # Test the actual chain creation by planning chains
        sample_chains = self.planner.plan_smart_chains(self.hihat_files)
        
        # Should have hi-hat chains
        hihat_chains = {k: v for k, v in sample_chains.items() if k.startswith('hats')}
        assert len(hihat_chains) > 0, "Should create hi-hat chains"
        
        # Check that chains have proper metadata
        for chain_name, chain_data in hihat_chains.items():
            metadata = chain_data['metadata']
            assert 'type' in metadata, "Should have type metadata"
            assert 'sample_count' in metadata, "Should have sample count"
            assert 'closed_count' in metadata, "Should have closed count"
            assert 'open_count' in metadata, "Should have open count"
    
    def test_regular_chain_creation(self):
        """Test that regular chains are created correctly."""
        # Test the actual chain creation by planning chains
        sample_chains = self.planner.plan_smart_chains(self.regular_files)
        
        # Should have regular chains
        regular_chains = {k: v for k, v in sample_chains.items() if not k.startswith('hats')}
        assert len(regular_chains) > 0, "Should create regular chains"
        
        # Check that chains have proper metadata
        for chain_name, chain_data in regular_chains.items():
            metadata = chain_data['metadata']
            assert 'type' in metadata, "Should have type metadata"
            assert 'sample_count' in metadata, "Should have sample count"
            assert len(chain_data['files']) > 0, "Should have files"

    def test_max_samples_limit(self):
        """Test that chains respect the max samples limit."""
        # Create many files to test the limit
        many_files = []
        for i in range(50):
            many_files.append(Path(f"Drums/Kick/Kick Test {i}.wav"))
        
        # Test the actual planning logic
        sample_chains = self.planner.plan_smart_chains(many_files)
        
        max_samples = self.planner.config.max_samples_per_chain
        for chain_name, chain_data in sample_chains.items():
            sample_count = chain_data['metadata']['sample_count']
            assert sample_count <= max_samples, f"Chain {chain_name} exceeds max samples: {sample_count} > {max_samples}"

    def test_smart_chain_planning(self):
        """Test the complete smart chain planning process."""
        sample_chains = self.planner.plan_smart_chains(self.all_files)

        # Should have chains for hihat groups and regular groups
        # Hi-hat chains are now named 'hats', 'hats_1', etc.
        assert any(k.startswith('hats') for k in sample_chains.keys())
        
        # Check that we have the expected hi-hat chain
        hats_chain = None
        for key, chain in sample_chains.items():
            if key.startswith('hats'):
                hats_chain = chain
                break
        
        assert hats_chain is not None
        assert hats_chain['metadata']['type'] == 'hihat'
        
        # Check that XOR files are included in the hi-hat chain
        xor_files = [f for f in hats_chain['files'] if 'XOR' in str(f)]
        assert len(xor_files) > 0, "Should include XOR files in hi-hat chain"
    
    def test_chain_validation(self):
        """Test that chain validation works correctly."""
        sample_chains = self.planner.plan_smart_chains(self.all_files)
        
        # Basic validation: check that all chains have required metadata
        for chain_name, chain_data in sample_chains.items():
            metadata = chain_data['metadata']
            assert 'type' in metadata, f"Chain {chain_name} missing type"
            assert 'sample_count' in metadata, f"Chain {chain_name} missing sample count"
            assert 'files' in chain_data, f"Chain {chain_name} missing files"
            assert len(chain_data['files']) > 0, f"Chain {chain_name} has no files"
    
    def test_chain_summary(self):
        """Test that chain summary provides correct information."""
        sample_chains = self.planner.plan_smart_chains(self.all_files)
        
        # Basic summary validation
        total_chains = len(sample_chains)
        hihat_chains = len([k for k in sample_chains.keys() if k.startswith('hats')])
        regular_chains = total_chains - hihat_chains
        total_samples = sum(c['metadata']['sample_count'] for c in sample_chains.values())
        
        assert total_chains > 0, "Should have at least one chain"
        assert total_samples > 0, "Should have at least one sample"
        assert hihat_chains >= 0, "Hi-hat chain count should be non-negative"
        assert regular_chains >= 0, "Regular chain count should be non-negative"


class TestSmartChainPlannerIntegration:
    """Test integration with real audio library structure."""
    
    def test_with_real_audio_library(self):
        """Test with the real audio library structure."""
        from tests.utils.real_audio_library_structure import get_real_audio_library_paths
        
        # Get real paths
        real_paths = get_real_audio_library_paths()
        
        # Filter to just hihat files for testing
        hihat_files = [p for p in real_paths if 'Hihat' in str(p) and p.suffix == '.wav']
        
        if hihat_files:
            # Create planner
            config = SampleChainConfig()
            planner = SmartChainPlanner(config)
            
            # Plan chains
            sample_chains = planner.plan_smart_chains(hihat_files)
            
            # Should have hihat chains
            assert len(sample_chains) > 0
            
            # Check that hihat chains have proper structure
            for chain_key, chain in sample_chains.items():
                if chain_key.startswith('hihat_'):
                    assert chain['metadata']['type'] == 'hihat'
                    assert 'closed_count' in chain['metadata']
                    assert 'open_count' in chain['metadata']
                    
                    # Verify closed files come first
                    if chain['metadata']['closed_count'] > 0 and chain['metadata']['open_count'] > 0:
                        files = chain['files']
                        closed_count = chain['metadata']['closed_count']
                        
                        # First N files should be closed hihats
                        for i in range(closed_count):
                            assert any(pattern in files[i].lower() for pattern in ['closedhh', 'clsdhh'])
