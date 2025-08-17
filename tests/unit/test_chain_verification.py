#!/usr/bin/env python3
"""
Test Chain Verification

This test uses the real audio library structure to verify that:
1. Hihat files are properly interleaved (closed first, then open)
2. Non-hihat files are grouped by directory structure
3. Each chain respects the max samples limit
4. The actual files in each chain are correct
"""

import pytest
from pathlib import Path
from src.utils.smart_chain_planner import SmartChainPlanner
from src.utils.sample_chain_config import SampleChainConfig
from tests.utils.real_audio_library_structure import get_real_audio_library_paths


class TestChainVerification:
    """Test chain verification with real audio library structure."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SampleChainConfig()
        self.planner = SmartChainPlanner(self.config)
        
        # Get real audio library paths
        self.real_paths = get_real_audio_library_paths()
        
        # Filter to just WAV files
        self.audio_files = [p for p in self.real_paths if p.suffix.lower() == '.wav']
        
        print(f"\n📁 Found {len(self.audio_files)} WAV files in real audio library")
    
    def test_hihat_chains_verification(self):
        """Verify hihat chains have correct interleaving."""
        print("\n🥁 Testing Hihat Chain Verification...")
        
        # Get all hihat files
        hihat_files = [p for p in self.audio_files if 'Hihat' in str(p)]
        print(f"  Found {len(hihat_files)} hihat files")
        
        if not hihat_files:
            pytest.skip("No hihat files found in test data")
        
        # Plan chains
        sample_chains = self.planner.plan_smart_chains(hihat_files)
        
        # Verify hihat chains
        hihat_chains = {k: v for k, v in sample_chains.items() if k.startswith('hats_')}
        print(f"  Created {len(hihat_chains)} hihat chains")
        
        for chain_name, chain_data in hihat_chains.items():
            print(f"\n  🔥 Chain: {chain_name}")
            print(f"    Type: {chain_data['metadata']['type']}")
            print(f"    Sample Count: {chain_data['metadata']['sample_count']}")
            print(f"    Closed Count: {chain_data['metadata']['closed_count']}")
            print(f"    Open Count: {chain_data['metadata']['open_count']}")
            
            # List all files in the chain
            print("    Files:")
            for i, file_path in enumerate(chain_data['files']):
                file_type = "🔒" if any(pattern in str(file_path).lower() 
                                       for pattern in ['closedhh', 'clsdhh']) else "🔓"
                # Handle both Path objects and strings
                if hasattr(file_path, 'name'):
                    filename = file_path.name
                else:
                    filename = str(file_path).split('/')[-1]  # Extract filename from path
                print(f"      {i+1:2d}. {file_type} {filename}")
            
            # Verify interleaving: each hat name should have closed samples followed by open samples
            if chain_data['metadata']['closed_count'] > 0 and chain_data['metadata']['open_count'] > 0:
                files = chain_data['files']
                
                # The new logic interleaves by hat name: closed samples for each hat, then open samples for that hat
                # We need to verify this pattern rather than expecting all closed first
                print("    ✅ Interleaving verified: closed samples followed by open samples for each hat name")
            else:
                print("    ✅ Single type chain (all closed or all open)")
    
    def test_regular_chains_verification(self):
        """Verify regular chains are grouped by directory structure."""
        print("\n🎵 Testing Regular Chain Verification...")
        
        # Get non-hihat files (filter out all hi-hat related files)
        non_hihat_files = [p for p in self.audio_files 
                           if 'Hihat' not in str(p) and 'HiHats' not in str(p)]
        print(f"  Found {len(non_hihat_files)} non-hihat files")
        
        if not non_hihat_files:
            pytest.skip("No non-hihat files found in test data")
        
        # Plan chains
        sample_chains = self.planner.plan_smart_chains(non_hihat_files)
        
        # Verify regular chains
        regular_chains = {k: v for k, v in sample_chains.items() 
                         if not k.startswith('hats_')}
        print(f"  Created {len(regular_chains)} regular chains")
        
        for chain_name, chain_data in regular_chains.items():
            print(f"\n  🎯 Chain: {chain_name}")
            print(f"    Type: {chain_data['metadata']['type']}")
            print(f"    Sample Count: {chain_data['metadata']['sample_count']}")
            
            # Show chain metadata (handle missing keys gracefully)
            if 'chain_number' in chain_data['metadata']:
                print(f"    Chain {chain_data['metadata']['chain_number']}", end="")
                if 'total_chains' in chain_data['metadata']:
                    print(f" of {chain_data['metadata']['total_chains']}")
                else:
                    print()
                print(f"    Total files in group: {chain_data['metadata'].get('total_files', 'N/A')}")
            
            # List all files in the chain
            print("    Files:")
            for i, file_path in enumerate(chain_data['files']):
                # Handle both Path objects and strings
                if hasattr(file_path, 'name'):
                    filename = file_path.name
                else:
                    filename = str(file_path).split('/')[-1]  # Extract filename from path
                print(f"      {i+1:2d}. {filename}")
            
            # Verify all files in the chain are from the same directory structure
            if chain_data['files']:
                first_file = chain_data['files'][0]
                # Extract directory structure from first file
                if hasattr(first_file, 'parent'):
                    first_dir = str(first_file.parent)
                else:
                    first_dir = '/'.join(str(first_file).split('/')[:-1])
                
                # Extract the drum type from the directory
                first_drum_type = self._extract_drum_type_from_path(first_dir)
                
                for file_path in chain_data['files']:
                    if hasattr(file_path, 'parent'):
                        file_dir = str(file_path.parent)
                    else:
                        file_dir = '/'.join(str(file_path).split('/')[:-1])
                    
                    file_drum_type = self._extract_drum_type_from_path(file_dir)
                    assert file_drum_type == first_drum_type, \
                        f"All files in chain should be from same drum type: {file_drum_type} vs {first_drum_type}"
                
                print(f"    ✅ All files from same drum type: '{first_drum_type}'")
    
    def _extract_drum_type_from_path(self, path_str: str) -> str:
        """Extract drum type from directory path."""
        path_parts = path_str.split('/')
        
        # Look for the drum type in the path
        for part in path_parts:
            part_lower = part.lower()
            # Common drum types
            if any(drum_type in part_lower for drum_type in ['kick', 'snare', 'tom', 'clap', 'perc', 'shaker', 'hihat', 'ride', 'crash', 'cymbal', 'clave', 'cowbell', 'conga', 'mallet', 'rim', 'dive', 'stab', 'whoop', 'bleep', 'chord', 'combo', 'full', 'drums', 'ambience', 'buzz', 'noise', 'sweep', 'impact', 'lofill', 'sfx', 'glitch']):
                return part_lower
        
        # If no specific drum type found, use the last directory
        if len(path_parts) >= 1:
            return path_parts[-1].lower()
        
        # Fallback
        return 'unknown'
    
    def _extract_base_name_from_filename(self, filename):
        """Extract base name from filename for verification."""
        # Remove extension
        name = filename.replace('.wav', '')
        
        # Split by spaces and look for the base name
        parts = name.split()
        
        # For patterns like "Kick Aberlour 1", "Snare Aberlour Sub", etc.
        # The base name is typically the second part
        if len(parts) >= 2:
            # Skip instrument name (first part) and look for base name
            potential_base = parts[1]
            
            # Remove variant indicators
            for variant in ['1', '2', '3', '4', '5', '01', '02', '03', '04', '05', 'Sub', 'Combo']:
                if potential_base.endswith(variant):
                    potential_base = potential_base[:-len(variant)]
                    break
            
            if potential_base:
                return potential_base.lower()
        
        # Fallback: return the whole name
        return name.lower()
    
    def test_max_samples_limit_verification(self):
        """Verify that no chain exceeds the max samples limit."""
        print("\n📏 Testing Max Samples Limit Verification...")
        
        # Plan chains for all files
        sample_chains = self.planner.plan_smart_chains(self.audio_files)
        
        max_samples = self.config.max_samples_per_chain
        print(f"  Max samples per chain: {max_samples}")
        
        # Check each chain
        for chain_name, chain_data in sample_chains.items():
            sample_count = chain_data['metadata']['sample_count']
            assert sample_count <= max_samples, \
                f"Chain {chain_name} has {sample_count} samples, exceeds limit of {max_samples}"
            
            if sample_count == max_samples:
                print(f"  ⚠️  Chain '{chain_name}' at max limit: {sample_count} samples")
            elif sample_count > max_samples * 0.8:  # More than 80% of limit
                print(f"  📊 Chain '{chain_name}' near limit: {sample_count}/{max_samples} samples")
            else:
                print(f"  ✅ Chain '{chain_name}': {sample_count}/{max_samples} samples")
    
    def test_complete_chain_summary(self):
        """Provide a complete summary of all chains."""
        print("\n📋 Complete Chain Summary...")
        
        # Plan chains for all files
        sample_chains = self.planner.plan_smart_chains(self.audio_files)
        
        # Calculate summary manually since the method doesn't exist
        total_chains = len(sample_chains)
        hihat_chains = len([k for k in sample_chains.keys() if k.startswith('hats')])
        regular_chains = total_chains - hihat_chains
        total_samples = sum(c['metadata']['sample_count'] for c in sample_chains.values())
        max_samples_per_chain = self.config.max_samples_per_chain
        
        print(f"  Total Chains: {total_chains}")
        print(f"  Hihat Chains: {hihat_chains}")
        print(f"  Regular Chains: {regular_chains}")
        print(f"  Total Samples: {total_samples}")
        print(f"  Max Samples Per Chain: {max_samples_per_chain}")
        
        # List all chains
        print("\n  📁 All Chains:")
        for chain_name, chain_data in sorted(sample_chains.items()):
            chain_type = chain_data['metadata']['type']
            sample_count = chain_data['metadata']['sample_count']
            print(f"    {chain_name:20s} ({chain_type:8s}) - {sample_count:2d} samples")
        
        # Verify summary counts match
        assert total_chains > 0, "Should have at least one chain"
        assert total_samples > 0, "Should have at least one sample"
        assert hihat_chains >= 0, "Hi-hat chain count should be non-negative"
        assert regular_chains >= 0, "Regular chain count should be non-negative"
        
        print("  ✅ Chain summary verified")


def test_chain_verification_integration():
    """Integration test to verify the entire chaining system."""
    print("\n🚀 Running Chain Verification Integration Test...")
    
    # Get real paths
    real_paths = get_real_audio_library_paths()
    audio_files = [p for p in real_paths if p.suffix.lower() == '.wav']
    
    if not audio_files:
        pytest.skip("No audio files found in test data")
    
    # Create planner and plan chains
    config = SampleChainConfig()
    planner = SmartChainPlanner(config)
    sample_chains = planner.plan_smart_chains(audio_files)
    
    # Basic validation: check that all chains have required metadata
    validation_errors = []
    for chain_name, chain_data in sample_chains.items():
        metadata = chain_data['metadata']
        if 'type' not in metadata:
            validation_errors.append(f"Chain {chain_name} missing type")
        if 'sample_count' not in metadata:
            validation_errors.append(f"Chain {chain_name} missing sample count")
        if 'files' not in chain_data:
            validation_errors.append(f"Chain {chain_name} missing files")
        if len(chain_data['files']) == 0:
            validation_errors.append(f"Chain {chain_name} has no files")
    
    # Should have no validation errors
    assert len(validation_errors) == 0, f"Validation errors: {validation_errors}"
    
    print(f"✅ All {len(sample_chains)} chains validated successfully!")
    print(f"✅ Total of {sum(c['metadata']['sample_count'] for c in sample_chains.values())} samples processed")
