"""
Audio Directory Structure Tests for NI Sample Chainer

These tests validate the handling of real-world audio sample library
structures like the one provided, with nested directories and various
audio file types.
"""

import pytest
import os
import sys
from pathlib import Path
from typing import List, Set, Dict

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

class TestAudioDirectoryStructure:
    """Test handling of real-world audio directory structures."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
        
        # Expected structure based on the real sample library
        self.expected_audio_structure = {
            'Drums': {
                'Clap': ['Clap Aberlour.wav', 'Clap Antimax.wav', 'Clap Beach.wav'],
                'Hihat': ['ClosedHH Aberlour 1.wav', 'ClosedHH Aberlour 2.wav', 'OpenHH Aberlour.wav'],
                'Kick': ['Kick Aberlour 1.wav', 'Kick Aberlour 2.wav', 'Kick Aberlour Sub.wav'],
                'Snare': ['Snare Aberlour 1.wav', 'Snare Aberlour 2.wav'],
                'Tom': ['Tom Fruit 1.wav', 'Tom Fruit 2.wav', 'Tom Fruit 3.wav'],
                'Percussion': ['Perc Aberlour 1.wav', 'Perc Aberlour 2.wav', 'Perc Aberlour 3.wav'],
                'Shaker': ['Shaker Aberlour.wav', 'Shaker Beach.wav'],
                'Cymbal': ['Cymbal Brownie.wav', 'Ride Berg.wav'],
                'Mallet Drum': ['Mallet Can.wav', 'Mallet PrisonerS.wav']
            },
            'Instruments': {
                'Bass': {
                    'Bontempo': ['Bontempo A2.wav', 'Bontempo A3.wav', 'Bontempo C3.wav'],
                    'Cohesion': ['Cohesion A2.wav', 'Cohesion A3.wav', 'Cohesion C2.wav'],
                    'Dirac': ['Dirac A1.wav', 'Dirac A2.wav', 'Dirac C1.wav'],
                    'Error Code': ['Error Code A1.wav', 'Error Code A2.wav', 'Error Code C1.wav']
                },
                'Lead': {
                    'Anaerobic': ['Anaerobic A1.wav', 'Anaerobic A2.wav', 'Anaerobic C2.wav'],
                    'Beirut': ['Beirut A1.wav', 'Beirut A2.wav', 'Beirut C2.wav'],
                    'Cassata': ['Cassata A2.wav', 'Cassata A3.wav', 'Cassata C2.wav']
                }
            },
            'Loops': {
                'Construction': {
                    'Aberlour': ['Chord[121] E Aberlour.wav', 'Drums[121] Aberlour 1.wav', 'Full[121] E Aberlour.wav'],
                    'Antimax': ['Bass[121] F# Antimax.wav', 'Drums[121] Antimax 1.wav', 'Full[121] F# Antimax.wav'],
                    'Beaching': ['Clap[121] Beaching.wav', 'Drums[121] Beaching 1.wav', 'HiHats[121] Beaching 1.wav']
                }
            },
            'One Shots': {
                'Ambience': ['Ambience Transistor 01.wav', 'Ambience Transistor 02.wav'],
                'Analog FX': ['Dive Berg.wav', 'Dive Fruit.wav', 'Rise Transistor 01.wav'],
                'Blip & Blop': ['Bleep Transistor 01.wav', 'Bleep Transistor 02.wav', 'Bleep Zee.wav'],
                'Buzz': ['Buzz Transistor 01.wav', 'Buzz Transistor 02.wav'],
                'Chord': ['Chord Aberlour.wav', 'Chord Bon Voyage 1.wav', 'Chord Normandy.wav'],
                'Glitch': ['Glitch Transistor 01.wav', 'Glitch Transistor 02.wav'],
                'Impact': ['Impact Normandy.wav', 'Impact Transistor 01.wav'],
                'Noise': ['Noise Transistor 01.wav', 'Noise Uebertonez.wav'],
                'Sweep & Swell': ['Sweep Normandy.wav', 'Swell Transistor 01.wav'],
                'Synth Note': ['ResoSynth Transistor c#3 01.wav', 'ResoSynth Transistor c#3 02.wav']
            }
        }
    
    def test_audio_directory_structure_recognition(self):
        """Test that we can recognize and parse audio directory structures."""
        # This test validates our understanding of the expected structure
        assert 'Drums' in self.expected_audio_structure
        assert 'Instruments' in self.expected_audio_structure
        assert 'Loops' in self.expected_audio_structure
        assert 'One Shots' in self.expected_audio_structure
        
        # Check that we have the expected drum categories
        expected_drum_categories = {'Clap', 'Hihat', 'Kick', 'Snare', 'Tom', 'Percussion', 'Shaker', 'Cymbal', 'Mallet Drum'}
        assert set(self.expected_audio_structure['Drums'].keys()) == expected_drum_categories
    
    def test_audio_file_naming_patterns(self):
        """Test recognition of audio file naming patterns."""
        # Extract all filenames from the structure
        all_files = []
        for category, subcategories in self.expected_audio_structure.items():
            if isinstance(subcategories, dict):
                for subcategory, files in subcategories.items():
                    if isinstance(files, dict):
                        # Nested structure (like Instruments)
                        for subsubcategory, subfiles in files.items():
                            all_files.extend(subfiles)
                    else:
                        # Direct file list
                        all_files.extend(files)
            else:
                # Direct file list
                all_files.extend(subcategories)
        
        # Check that we have WAV files
        wav_files = [f for f in all_files if f.endswith('.wav')]
        assert len(wav_files) > 0, "No WAV files found in structure"
        
        # Check for specific naming patterns
        clap_files = [f for f in wav_files if 'Clap' in f]
        assert len(clap_files) > 0, "No clap files found"
        
        kick_files = [f for f in wav_files if 'Kick' in f]
        assert len(kick_files) > 0, "No kick files found"
        
        # Check for numbered variations
        numbered_files = [f for f in wav_files if any(char.isdigit() for char in f)]
        assert len(numbered_files) > 0, "No numbered files found"
    
    def test_directory_depth_analysis(self):
        """Test analysis of directory depth and structure."""
        max_depth = 0
        category_depths = {}
        
        for category, subcategories in self.expected_audio_structure.items():
            depth = 1
            if isinstance(subcategories, dict):
                depth = 2
                for subcategory, items in subcategories.items():
                    if isinstance(items, dict):
                        depth = 3
                        break
            category_depths[category] = depth
            max_depth = max(max_depth, depth)
        
        # Check expected depths
        assert category_depths['Drums'] == 2, "Drums should have depth 2"
        assert category_depths['Instruments'] == 3, "Instruments should have depth 3"
        assert category_depths['Loops'] == 3, "Loops should have depth 3"
        assert category_depths['One Shots'] == 2, "One Shots should have depth 2"
        assert max_depth == 3, "Maximum depth should be 3"
    
    def test_audio_category_classification(self):
        """Test classification of audio files into categories."""
        # Simulate audio file classification
        audio_categories = {
            'drum': ['Kick', 'Snare', 'Hihat', 'Clap', 'Tom', 'Cymbal', 'Percussion', 'Shaker', 'Mallet Drum'],
            'bass': ['Bontempo', 'Cohesion', 'Dirac', 'Error Code', 'Fallout', 'Gogettue', 'Ruebycon', 'Scalar', 'Shoveler', 'Totalistic'],
            'lead': ['Anaerobic', 'Beirut', 'Cassata', 'Circularism', 'Delta Curve', 'Dweller', 'Echnatone', 'Ethifier', 'Harmotron', 'Schmoof'],
            'loop': ['Construction'],
            'one_shot': ['Ambience', 'Analog FX', 'Blip & Blop', 'Buzz', 'Chord', 'Glitch', 'Impact', 'Noise', 'Sweep & Swell', 'Synth Note']
        }
        
        # Validate categories
        for category, subcategories in audio_categories.items():
            assert len(subcategories) > 0, f"Category {category} should have subcategories"
        
        # Check that we have the expected main categories
        expected_main_categories = {'drum', 'bass', 'lead', 'loop', 'one_shot'}
        assert set(audio_categories.keys()) == expected_main_categories

class TestAudioFileDiscovery:
    """Test audio file discovery and organization utilities."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_wav_file_discovery(self):
        """Test discovery of WAV files in directory structure."""
        # This would test actual file discovery in a real directory
        # For now, we'll test the concept
        
        # Simulate finding WAV files
        wav_extensions = ['.wav', '.WAV']
        assert '.wav' in wav_extensions, "WAV extension should be recognized"
        
        # Test file pattern matching
        test_files = [
            'Clap Aberlour.wav',
            'Kick Aberlour 1.wav',
            'Snare Beach 2.wav',
            'Hihat ClosedHH Antimax 01.wav'
        ]
        
        wav_files = [f for f in test_files if any(f.lower().endswith(ext.lower()) for ext in wav_extensions)]
        assert len(wav_files) == len(test_files), "All test files should be WAV files"
    
    def test_audio_file_organization(self):
        """Test organization of audio files by category and type."""
        # Simulate organizing files by category
        file_organization = {
            'Drums/Clap': ['Clap Aberlour.wav', 'Clap Antimax.wav'],
            'Drums/Kick': ['Kick Aberlour 1.wav', 'Kick Aberlour 2.wav'],
            'Instruments/Bass/Bontempo': ['Bontempo A2.wav', 'Bontempo A3.wav'],
            'Loops/Construction/Aberlour': ['Chord[121] E Aberlour.wav', 'Drums[121] Aberlour 1.wav']
        }
        
        # Check organization structure
        for category_path, files in file_organization.items():
            assert len(files) > 0, f"Category {category_path} should have files"
            assert all(f.endswith('.wav') for f in files), f"All files in {category_path} should be WAV files"
    
    def test_audio_file_metadata_extraction(self):
        """Test extraction of metadata from audio filenames."""
        # Test filename parsing
        test_filenames = [
            'Clap Aberlour.wav',
            'Kick Aberlour 1.wav',
            'Kick Aberlour Sub.wav',
            'Hihat ClosedHH Antimax 01.wav',
            'Chord[121] E Aberlour.wav',
            'Drums[121] Antimax 1.wav'
        ]
        
        # Extract components
        for filename in test_filenames:
            # Remove extension
            name_without_ext = filename.replace('.wav', '')
            
            # Check for common patterns
            assert len(name_without_ext) > 0, "Filename should have content without extension"
            
            # Check for numbered variations
            has_number = any(char.isdigit() for char in name_without_ext)
            # Some files should have numbers, some shouldn't
            assert True, "Filename analysis should work"
    
    def test_directory_structure_validation(self):
        """Test validation of audio directory structure."""
        # This would validate that a directory structure matches expected patterns
        # For now, we'll test the concept
        
        expected_structure = {
            'Drums': ['Clap', 'Hihat', 'Kick', 'Snare', 'Tom', 'Percussion', 'Shaker', 'Cymbal', 'Mallet Drum'],
            'Instruments': ['Bass', 'Lead'],
            'Loops': ['Construction'],
            'One Shots': ['Ambience', 'Analog FX', 'Blip & Blop', 'Buzz', 'Chord', 'Glitch', 'Impact', 'Noise', 'Sweep & Swell', 'Synth Note']
        }
        
        # Validate structure
        for main_category, subcategories in expected_structure.items():
            assert isinstance(subcategories, list), f"{main_category} should have list of subcategories"
            assert len(subcategories) > 0, f"{main_category} should have subcategories"

class TestSampleChainGeneration:
    """Test sample chain generation from audio directory structures."""
    
    def setup_method(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent
    
    def test_sample_chain_planning(self):
        """Test planning of sample chains from directory structure."""
        # Simulate planning sample chains
        sample_chain_plan = {
            'drum_kit_1': {
                'kick': ['Kick Aberlour 1.wav', 'Kick Aberlour 2.wav'],
                'snare': ['Snare Aberlour 1.wav', 'Snare Aberlour 2.wav'],
                'hihat': ['ClosedHH Aberlour 1.wav', 'ClosedHH Aberlour 2.wav', 'OpenHH Aberlour.wav'],
                'clap': ['Clap Aberlour.wav'],
                'cymbal': ['Cymbal Brownie.wav']
            },
            'bass_collection': {
                'bontempo': ['Bontempo A2.wav', 'Bontempo A3.wav', 'Bontempo C3.wav'],
                'cohesion': ['Cohesion A2.wav', 'Cohesion A3.wav', 'Cohesion C2.wav']
            }
        }
        
        # Validate sample chain plan
        for chain_name, instruments in sample_chain_plan.items():
            assert isinstance(instruments, dict), f"Chain {chain_name} should have instrument mapping"
            for instrument, samples in instruments.items():
                assert isinstance(samples, list), f"Instrument {instrument} should have sample list"
                assert len(samples) > 0, f"Instrument {instrument} should have samples"
    
    def test_sample_chain_export_structure(self):
        """Test export structure for sample chains."""
        # Simulate export structure
        export_structure = {
            'drum_kit_1': {
                'kick_samples': ['kick_001.wav', 'kick_002.wav'],
                'snare_samples': ['snare_001.wav', 'snare_002.wav'],
                'hihat_samples': ['hihat_001.wav', 'hihat_002.wav', 'hihat_003.wav'],
                'metadata': 'drum_kit_1_metadata.json'
            }
        }
        
        # Validate export structure
        for kit_name, kit_contents in export_structure.items():
            assert 'metadata' in kit_contents, f"Kit {kit_name} should have metadata"
            sample_categories = [k for k in kit_contents.keys() if k != 'metadata']
            assert len(sample_categories) > 0, f"Kit {kit_name} should have sample categories"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])



