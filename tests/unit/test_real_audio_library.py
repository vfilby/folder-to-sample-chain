"""
Tests for AudioDirectoryAnalyzer using real audio library structure.

These tests use the actual directory structure from a real audio library
to ensure the analyzer works correctly with real-world data.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from src.utils.audio_directory_analyzer import AudioDirectoryAnalyzer
from tests.utils.real_audio_library_structure import (
    get_real_audio_library_structure,
    get_real_audio_library_paths,
    get_real_audio_library_stats
)


class TestRealAudioLibraryAnalyzer:
    """Test AudioDirectoryAnalyzer with real audio library structure."""
    
    def setup_method(self):
        """Set up test data and temporary directory."""
        self.real_paths = get_real_audio_library_paths()
        self.real_stats = get_real_audio_library_stats()
        
        # Create temporary directory structure
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_temp_structure()
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def setup_temp_structure(self):
        """Create temporary directory structure based on real data."""
        # Create directories first
        for path in self.real_paths:
            if not path.suffix:  # Directory
                (self.temp_dir / path).mkdir(parents=True, exist_ok=True)
        
        # Create mock WAV files
        for path in self.real_paths:
            if path.suffix.lower() == '.wav':
                full_path = self.temp_dir / path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Create empty file
                full_path.touch()
    
    def test_real_library_stats_loaded(self):
        """Test that real library stats are correctly loaded."""
        assert self.real_stats['total_paths'] == 1241
        assert self.real_stats['total_files'] == 1164
        assert self.real_stats['total_directories'] == 77
        assert self.real_stats['drums_count'] == 540
        assert self.real_stats['instruments_count'] == 343
        assert self.real_stats['loops_count'] == 276
        assert self.real_stats['one_shots_count'] == 147
    
    def test_real_library_paths_loaded(self):
        """Test that real library paths are correctly loaded."""
        assert len(self.real_paths) == 1241
        
        # Check some specific paths exist
        drum_paths = [p for p in self.real_paths if 'Drums' in str(p)]
        assert len(drum_paths) == 540
        
        # Check specific drum categories
        clap_paths = [p for p in self.real_paths if 'Clap' in str(p) and p.suffix == '.wav']
        assert len(clap_paths) > 0
        
        kick_paths = [p for p in self.real_paths if 'Kick' in str(p) and p.suffix == '.wav']
        assert len(kick_paths) > 0
    
    def test_analyzer_with_real_structure(self):
        """Test AudioDirectoryAnalyzer with real library structure."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        
        # Test directory structure
        structure = analyzer.get_directory_structure()
        assert 'Drums' in structure
        assert 'Instruments' in structure
        assert 'Loops' in structure
        assert 'One Shots' in structure
        
        # Test file discovery
        audio_files = analyzer.get_audio_files()
        assert len(audio_files) == 1164
        
        # Test categorization
        categories = analyzer.get_file_categories()
        assert 'drum' in categories
        assert 'bass' in categories
        assert 'lead' in categories
        assert 'loop' in categories
        assert 'one_shot' in categories
        
        # Test category counts match analyzer results
        drums_count = len(analyzer.get_files_by_category('drum'))
        assert drums_count > 500  # Should be around 540-541
        
        bass_count = len(analyzer.get_files_by_category('bass'))
        assert bass_count > 150  # Should be around 173
        
        loops_count = len(analyzer.get_files_by_category('loop'))
        assert loops_count > 150  # Should be around 165
        
        lead_count = len(analyzer.get_files_by_category('lead'))
        assert lead_count > 100  # Should be around 149
        
        one_shot_count = len(analyzer.get_files_by_category('one_shot'))
        assert one_shot_count > 100  # Should be around 136
    
    def test_analyzer_category_summary(self):
        """Test category summary with real data."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        summary = analyzer.get_category_summary()
        
        # Check that categories exist and have reasonable counts
        assert summary['drum'] > 500  # Should be around 540-541
        assert summary['bass'] > 150  # Should be around 173
        assert summary['loop'] > 150  # Should be around 165
        assert summary['lead'] > 100  # Should be around 149
        assert summary['one_shot'] > 100  # Should be around 136
        
        # Check total matches expected
        total_files = sum(v for k, v in summary.items() if k != 'total')
        assert total_files == 1164
    
    def test_analyzer_directory_depth_analysis(self):
        """Test directory depth analysis with real structure."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        depth_analysis = analyzer.get_directory_depth_analysis()
        
        # Real structure has multiple levels
        assert max(depth_analysis.values()) >= 3
        assert min(depth_analysis.values()) >= 1
        
        # Check specific categories have expected depths
        assert depth_analysis['Drums'] >= 2  # Drums/Category/File
        assert depth_analysis['Instruments'] >= 3  # Instruments/Type/Instrument/File
        assert depth_analysis['Loops'] >= 3  # Loops/Type/Name/File
        assert depth_analysis['One Shots'] >= 2  # One Shots/Category/File
    
    def test_analyzer_sample_chain_planning(self):
        """Test sample chain planning with real data."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        sample_chains = analyzer.plan_sample_chains(max_samples_per_chain=10)
        
        # Should have chains for different instrument families
        assert len(sample_chains) > 0
        
        # Check that we have chains for different bass instruments
        bass_chains = [k for k in sample_chains.keys() if k.startswith('bass_')]
        assert len(bass_chains) > 0
        
        # Check that each chain has the expected structure
        for chain_name, chain_data in sample_chains.items():
            assert isinstance(chain_data, dict)
            assert 'metadata' in chain_data
            assert 'sample_count' in chain_data['metadata']
            assert chain_data['metadata']['sample_count'] > 0
    
    def test_analyzer_export_structure(self):
        """Test export structure generation with real data."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        sample_chains = analyzer.plan_sample_chains(max_samples_per_chain=10)
        export_structure = analyzer.generate_export_structure(sample_chains)
        
        assert 'sample_chains' in export_structure
        assert 'metadata' in export_structure
        assert 'export_settings' in export_structure
        
        # Check summary matches real data
        metadata = export_structure['metadata']
        assert metadata['total_files'] == 1164
        assert 'categories' in metadata
        
        # Check categories in metadata
        categories = metadata['categories']
        assert 'drum' in categories
        assert 'bass' in categories
        assert 'lead' in categories
        assert 'loop' in categories
        
        # Check export settings
        export_settings = export_structure['export_settings']
        assert 'sample_rate' in export_settings
        assert 'bit_depth' in export_settings
        assert 'format' in export_settings
    
    def test_analyzer_with_real_file_patterns(self):
        """Test analyzer correctly identifies real file patterns."""
        analyzer = AudioDirectoryAnalyzer(self.temp_dir)
        
        # Test specific drum patterns
        clap_files = [f for f in analyzer.get_audio_files() if 'Clap' in str(f)]
        assert len(clap_files) > 0
        
        # Test specific instrument patterns
        bass_files = [f for f in analyzer.get_audio_files() if 'Bass' in str(f)]
        assert len(bass_files) > 0
        
        # Test specific loop patterns
        construction_files = [f for f in analyzer.get_audio_files() if 'Construction' in str(f)]
        assert len(construction_files) > 0
        
        # Test specific one-shot patterns
        impact_files = [f for f in analyzer.get_audio_files() if 'Impact' in str(f)]
        assert len(impact_files) > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
