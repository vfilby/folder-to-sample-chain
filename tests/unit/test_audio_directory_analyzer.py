"""
Tests for Audio Directory Analyzer

These tests validate the audio directory analyzer utility
for processing real-world audio sample library structures.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from utils.audio_directory_analyzer import AudioDirectoryAnalyzer, analyze_audio_directory

class TestAudioDirectoryAnalyzer:
    """Test the AudioDirectoryAnalyzer class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.analyzer = None
        
        # Create test directory structure
        self._create_test_structure()
    
    def teardown_method(self):
        """Clean up test environment."""
        if self.analyzer:
            del self.analyzer
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def _create_test_structure(self):
        """Create a test directory structure with mock audio files."""
        # Create main categories
        (self.test_dir / 'Drums').mkdir()
        (self.test_dir / 'Instruments').mkdir()
        (self.test_dir / 'Loops').mkdir()
        (self.test_dir / 'One Shots').mkdir()
        
        # Create drum subcategories
        (self.test_dir / 'Drums' / 'Kick').mkdir()
        (self.test_dir / 'Drums' / 'Snare').mkdir()
        (self.test_dir / 'Drums' / 'Hihat').mkdir()
        (self.test_dir / 'Drums' / 'Clap').mkdir()
        
        # Create instrument subcategories
        (self.test_dir / 'Instruments' / 'Bass').mkdir()
        (self.test_dir / 'Instruments' / 'Lead').mkdir()
        (self.test_dir / 'Instruments' / 'Bass' / 'Bontempo').mkdir()
        (self.test_dir / 'Instruments' / 'Lead' / 'Anaerobic').mkdir()
        
        # Create loop subcategories
        (self.test_dir / 'Loops' / 'Construction').mkdir()
        (self.test_dir / 'Loops' / 'Construction' / 'Aberlour').mkdir()
        
        # Create one shot subcategories
        (self.test_dir / 'One Shots' / 'Ambience').mkdir()
        (self.test_dir / 'One Shots' / 'Analog FX').mkdir()
        
        # Create test audio files
        self._create_test_audio_files()
    
    def _create_test_audio_files(self):
        """Create test audio files with realistic names."""
        test_files = [
            # Drums
            'Drums/Kick/Kick Aberlour 1.wav',
            'Drums/Kick/Kick Aberlour 2.wav',
            'Drums/Kick/Kick Aberlour Sub.wav',
            'Drums/Snare/Snare Aberlour 1.wav',
            'Drums/Snare/Snare Aberlour 2.wav',
            'Drums/Hihat/ClosedHH Aberlour 1.wav',
            'Drums/Hihat/ClosedHH Aberlour 2.wav',
            'Drums/Hihat/OpenHH Aberlour.wav',
            'Drums/Clap/Clap Aberlour.wav',
            'Drums/Clap/Clap Antimax.wav',
            
            # Instruments
            'Instruments/Bass/Bontempo/Bontempo A2.wav',
            'Instruments/Bass/Bontempo/Bontempo A3.wav',
            'Instruments/Bass/Bontempo/Bontempo C3.wav',
            'Instruments/Lead/Anaerobic/Anaerobic A1.wav',
            'Instruments/Lead/Anaerobic/Anaerobic A2.wav',
            'Instruments/Lead/Anaerobic/Anaerobic C2.wav',
            
            # Loops
            'Loops/Construction/Aberlour/Chord[121] E Aberlour.wav',
            'Loops/Construction/Aberlour/Drums[121] Aberlour 1.wav',
            'Loops/Construction/Aberlour/Full[121] E Aberlour.wav',
            
            # One Shots
            'One Shots/Ambience/Ambience Transistor 01.wav',
            'One Shots/Ambience/Ambience Transistor 02.wav',
            'One Shots/Analog FX/Dive Berg.wav',
            'One Shots/Analog FX/Rise Transistor 01.wav'
        ]
        
        for file_path in test_files:
            full_path = self.test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            # Create a simple text file that simulates WAV data
            full_path.write_text(f"# Mock WAV file: {file_path}")
    
    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        assert analyzer.root_directory == self.test_dir
        assert len(analyzer.audio_files) > 0
        assert isinstance(analyzer.directory_structure, dict)
        assert isinstance(analyzer.file_categories, dict)
    
    def test_audio_file_discovery(self):
        """Test that audio files are discovered correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        # Should find all our test files
        expected_file_count = 23  # Based on our test structure
        assert len(analyzer.audio_files) == expected_file_count
        
        # Check that all files are WAV files
        for file_path in analyzer.audio_files:
            assert file_path.suffix.lower() == '.wav'
            assert file_path.exists()
    
    def test_directory_structure_building(self):
        """Test that directory structure is built correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        structure = analyzer.get_directory_structure()
        
        # Check main categories exist
        assert 'Drums' in structure
        assert 'Instruments' in structure
        assert 'Loops' in structure
        assert 'One Shots' in structure
        
        # Check subcategories
        assert 'Kick' in structure['Drums']
        assert 'Bontempo' in structure['Instruments']['Bass']
        assert 'Aberlour' in structure['Loops']['Construction']
    
    def test_file_categorization(self):
        """Test that files are categorized correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        categories = analyzer.get_file_categories()
        
        # Check that we have the expected categories
        assert 'drum' in categories
        assert 'bass' in categories
        assert 'lead' in categories
        assert 'loop' in categories
        assert 'one_shot' in categories
        
        # Check that files are in the right categories
        drum_files = categories['drum']
        assert len(drum_files) > 0
        assert any('Kick' in f for f in drum_files)
        assert any('Snare' in f for f in drum_files)
        assert any('Hihat' in f for f in drum_files)
        assert any('Clap' in f for f in drum_files)
    
    def test_category_summary(self):
        """Test that category summary is generated correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        summary = analyzer.get_category_summary()
        
        # Check that all categories have file counts
        for category, count in summary.items():
            assert count > 0, f"Category {category} should have files"
            assert isinstance(count, int), f"Count for {category} should be integer"
    
    def test_directory_depth_analysis(self):
        """Test that directory depth is analyzed correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        depth_analysis = analyzer.get_directory_depth_analysis()
        
        # Check expected depths (depth includes files as a level)
        assert depth_analysis['Drums'] == 3, "Drums should have depth 3 (including files)"
        assert depth_analysis['Instruments'] == 4, "Instruments should have depth 4 (including files)"
        assert depth_analysis['Loops'] == 4, "Loops should have depth 4 (including files)"
        assert depth_analysis['One Shots'] == 3, "One Shots should have depth 3 (including files)"
    
    def test_sample_chain_planning(self):
        """Test that sample chains are planned correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        sample_chains = analyzer.plan_sample_chains(max_samples_per_chain=5)
        
        # Check that we have sample chains
        assert len(sample_chains) > 0
        
        # Check drum kit chains
        drum_chains = {k: v for k, v in sample_chains.items() if k.startswith('drum_kit_')}
        assert len(drum_chains) > 0
        
        # Check instrument chains
        instrument_chains = {k: v for k, v in sample_chains.items() if k.startswith(('bass_', 'lead_'))}
        assert len(instrument_chains) > 0
    
    def test_export_structure_generation(self):
        """Test that export structure is generated correctly."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        sample_chains = analyzer.plan_sample_chains()
        
        export_structure = analyzer.generate_export_structure(sample_chains)
        
        # Check metadata
        assert 'metadata' in export_structure
        assert 'source_directory' in export_structure['metadata']
        assert 'total_files' in export_structure['metadata']
        assert 'categories' in export_structure['metadata']
        
        # Check sample chains
        assert 'sample_chains' in export_structure
        assert len(export_structure['sample_chains']) > 0
        
        # Check export settings
        assert 'export_settings' in export_structure
        assert export_structure['export_settings']['format'] == 'wav'
        assert export_structure['export_settings']['sample_rate'] == 44100
    
    def test_get_files_by_category(self):
        """Test getting files by specific category."""
        analyzer = AudioDirectoryAnalyzer(self.test_dir)
        
        drum_files = analyzer.get_files_by_category('drum')
        assert len(drum_files) > 0
        assert all('drum' in f.lower() or any(drum_term in f.lower() for drum_term in ['kick', 'snare', 'hihat', 'clap']) for f in drum_files)
        
        bass_files = analyzer.get_files_by_category('bass')
        assert len(bass_files) > 0
        assert all('bass' in f.lower() for f in bass_files)

class TestAudioDirectoryAnalyzerEdgeCases:
    """Test edge cases and error handling."""
    
    def test_nonexistent_directory(self):
        """Test handling of nonexistent directory."""
        nonexistent_dir = Path('/nonexistent/directory')
        
        with pytest.raises(ValueError, match="does not exist"):
            AudioDirectoryAnalyzer(nonexistent_dir)
    
    def test_empty_directory(self):
        """Test handling of empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = AudioDirectoryAnalyzer(temp_dir)
            
            assert len(analyzer.audio_files) == 0
            assert len(analyzer.get_file_categories()) == 0
            assert len(analyzer.get_directory_structure()) == 0
    
    def test_directory_without_audio_files(self):
        """Test handling of directory with no audio files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some non-audio files
            (Path(temp_dir) / 'readme.txt').write_text("Readme file")
            (Path(temp_dir) / 'config.json').write_text('{"key": "value"}')
            
            analyzer = AudioDirectoryAnalyzer(temp_dir)
            
            assert len(analyzer.audio_files) == 0
            assert len(analyzer.get_file_categories()) == 0
    
    def test_mixed_file_types(self):
        """Test handling of directory with mixed file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create mixed file types
            (temp_path / 'audio.wav').write_text("WAV file")
            (temp_path / 'audio.flac').write_text("FLAC file")
            (temp_path / 'audio.aiff').write_text("AIFF file")
            (temp_path / 'document.txt').write_text("Text file")
            (temp_path / 'image.jpg').write_text("Image file")
            
            analyzer = AudioDirectoryAnalyzer(temp_path)
            
            # Should find audio files but not text or image files
            assert len(analyzer.audio_files) == 3
            assert all(f.suffix.lower() in ['.wav', '.flac', '.aiff'] for f in analyzer.audio_files)

class TestConvenienceFunction:
    """Test the convenience function."""
    
    def test_analyze_audio_directory_function(self):
        """Test the analyze_audio_directory convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / 'test.wav').write_text("Test audio file")
            
            analyzer = analyze_audio_directory(temp_dir)
            
            assert isinstance(analyzer, AudioDirectoryAnalyzer)
            assert analyzer.root_directory == temp_path
            assert len(analyzer.audio_files) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
