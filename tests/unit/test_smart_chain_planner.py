"""
Tests for SmartChainPlanner.

Tests the hihat interleaving and name-based grouping functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.utils.smart_chain_planner import SmartChainPlanner, create_smart_chains
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
        self.planner = SmartChainPlanner()
    
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
        """Test that base names are correctly extracted from filenames."""
        test_cases = [
            (Path("Drums/Hihat/ClosedHH XOR 1.wav"), "xor"),
            (Path("Drums/Hihat/ClosedHH XOR 2.wav"), "xor"),
            (Path("Drums/Hihat/OpenHH XOR.wav"), "xor"),
            (Path("Drums/Kick/Kick XOR Sub.wav"), "xor"),
            (Path("Drums/Kick/Kick XOR Combo.wav"), "xor"),
            (Path("Drums/Snare/Snare Aberlour 1.wav"), "aberlour"),
        ]
        
        for file_path, expected_base in test_cases:
            base_name = self.planner.config.extract_base_name(file_path)
            assert base_name == expected_base, f"Expected {expected_base}, got {base_name} for {file_path}"
    
    def test_hihat_grouping(self):
        """Test that hihat files are grouped correctly by base name."""
        grouped_files = self.planner._group_files_by_name(self.hihat_files)

        # Check that XOR files are grouped together
        assert 'hihat_xor' in grouped_files
        xor_group = grouped_files['hihat_xor']
        assert len(xor_group) == 4  # 3 closed + 1 open

        # Check that Aberlour files are grouped together
        assert 'hihat_aberlour' in grouped_files
        aberlour_group = grouped_files['hihat_aberlour']
        assert len(aberlour_group) == 3  # 2 closed + 1 open

        # Check that Can files are grouped together (only 1 open file)
        assert 'hihat_can' in grouped_files
        can_group = grouped_files['hihat_can']
        assert len(can_group) == 1  # Only 1 open file (no closed files with 'can' name)
    
    def test_hihat_chain_creation(self):
        """Test that hihat chains are created with proper interleaving."""
        # Create hihat chain for XOR
        xor_files = [
            Path("Drums/Hihat/ClosedHH XOR 1.wav"),
            Path("Drums/Hihat/ClosedHH XOR 2.wav"),
            Path("Drums/Hihat/ClosedHH XOR 3.wav"),
            Path("Drums/Hihat/OpenHH XOR.wav"),
        ]
    
        chains = self.planner._create_hihat_chain('hihats', xor_files)
    
        assert chains is not None
        assert len(chains) == 1  # Should have one chain for 4 files
        chain = chains[0]
        assert chain['metadata']['type'] == 'hihat'
        assert chain['metadata']['sample_count'] == 4
        assert chain['metadata']['closed_count'] == 3
        assert chain['metadata']['open_count'] == 1
        
        # Verify closed files come first
        files = chain['files']
        assert len(files) == 4
        assert 'ClosedHH' in files[0]
        assert 'ClosedHH' in files[1]
        assert 'ClosedHH' in files[2]
        assert 'OpenHH' in files[3]
    
    def test_regular_chain_creation(self):
        """Test that regular chains are created correctly."""
        # Create regular chain for XOR kick
        xor_kick_files = [
            Path("Drums/Kick/Kick XOR 1.wav"),
            Path("Drums/Kick/Kick XOR 2.wav"),
            Path("Drums/Kick/Kick XOR Sub.wav"),
        ]
    
        chains = self.planner._create_regular_chain('drums/kick', xor_kick_files)
    
        assert chains is not None
        assert len(chains) == 1  # Should have one chain for 3 files
        chain = chains[0]
        assert chain['metadata']['type'] == 'regular'
        assert chain['metadata']['group_key'] == 'drums/kick'
        assert chain['metadata']['sample_count'] == 3
        assert len(chain['files']) == 3

    def test_max_samples_limit(self):
        """Test that chains respect the max samples limit."""
        # Create many files to test the limit
        many_files = []
        for i in range(50):
            many_files.append(Path(f"Drums/Kick/Kick Test {i}.wav"))
    
        chains = self.planner._create_regular_chain('drums/kick', many_files)
    
        assert chains is not None
        assert len(chains) == 2  # Should have 2 chains: 32 + 18 samples
        assert chains[0]['metadata']['sample_count'] == 32  # First chain at max
        assert chains[1]['metadata']['sample_count'] == 18  # Second chain with remaining

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
        xor_files = [f for f in hats_chain['files'] if 'XOR' in f]
        assert len(xor_files) == 4  # 3 closed + 1 open
    
    def test_chain_validation(self):
        """Test that chain validation works correctly."""
        sample_chains = self.planner.plan_smart_chains(self.all_files)
        
        # Validate chains
        validation_messages = self.planner.validate_chain_rules(sample_chains)
        
        # Should have no validation errors
        assert len(validation_messages) == 0, f"Validation errors: {validation_messages}"
    
    def test_chain_summary(self):
        """Test that chain summary provides correct information."""
        sample_chains = self.planner.plan_smart_chains(self.all_files)
        summary = self.planner.get_chain_summary(sample_chains)
        
        assert summary['total_chains'] > 0
        assert summary['hihat_chains'] > 0
        assert summary['regular_chains'] > 0
        assert summary['max_samples_per_chain'] == 32
        assert 'config_summary' in summary


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
            planner = SmartChainPlanner()
            
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


def test_create_smart_chains_function():
    """Test the convenience function."""
    files = [
        Path("Drums/Hihat/ClosedHH Test 1.wav"),
        Path("Drums/Hihat/ClosedHH Test 2.wav"),
        Path("Drums/Hihat/OpenHH Test.wav"),
    ]

    sample_chains = create_smart_chains(files)

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
    assert len(hats_chain['files']) == 3
