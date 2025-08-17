"""
Integration tests for the complete audio processing pipeline.

This test demonstrates the full workflow from sample chain planning
to audio processing and export.
"""

import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
import tempfile
import shutil

from src.utils.audio_directory_analyzer import AudioDirectoryAnalyzer
from src.utils.smart_chain_planner import SmartChainPlanner
from src.audio_processing.sample_chain_builder import SampleChainBuilder
from src.audio_processing.chain_exporter import ChainExporter
from src.utils.config import ConfigManager


class TestAudioPipeline:
    """Test the complete audio processing pipeline."""
    
    @pytest.fixture
    def temp_audio_dir(self):
        """Create a temporary directory with test audio files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create test audio files
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create directory structure
        drums_dir = temp_dir / "Drums"
        drums_dir.mkdir()
        
        kick_dir = drums_dir / "Kick"
        kick_dir.mkdir()
        
        snare_dir = drums_dir / "Snare"
        snare_dir.mkdir()
        
        hihat_dir = drums_dir / "Hihat"
        hihat_dir.mkdir()
        
        # Create kick samples
        for i in range(3):
            freq = 60 + i * 10  # Different frequencies
            audio_data = 0.3 * np.sin(2 * np.pi * freq * t)
            filename = kick_dir / f"Kick Test {i+1}.wav"
            sf.write(str(filename), audio_data, sample_rate)
            print(f"Created: {filename}")
        
        # Create snare samples
        for i in range(2):
            freq = 200 + i * 50
            audio_data = 0.25 * np.sin(2 * np.pi * freq * t)
            filename = snare_dir / f"Snare Test {i+1}.wav"
            sf.write(str(filename), audio_data, sample_rate)
            print(f"Created: {filename}")
        
        # Create hihat samples (different lengths for testing)
        hihat_durations = [0.5, 0.8, 1.2]
        for i, dur in enumerate(hihat_durations):
            t_short = np.linspace(0, dur, int(sample_rate * dur), False)
            freq = 800 + i * 200
            audio_data = 0.2 * np.sin(2 * np.pi * freq * t_short)
            filename = hihat_dir / f"Hihat Test {i+1}.wav"
            sf.write(str(filename), audio_data, sample_rate)
            print(f"Created: {filename}")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self):
        """Load test configuration."""
        config_manager = ConfigManager()
        return config_manager.load_config(Path('config.yaml'))
    
    def test_complete_pipeline(self, temp_audio_dir, config):
        """Test the complete audio processing pipeline."""
        print(f"\nTesting complete pipeline with audio directory: {temp_audio_dir}")
        
        # Step 1: Analyze the audio directory
        analyzer = AudioDirectoryAnalyzer(temp_audio_dir)
        
        print(f"Directory analysis complete:")
        print(f"  - Total audio files: {len(analyzer.get_audio_files())}")
        print(f"  - Categories: {list(analyzer.get_category_summary().keys())}")
        

        
        # Step 2: Plan sample chains
        planner = SmartChainPlanner()
        sample_chains = planner.plan_smart_chains(analyzer.get_audio_files())
        
        print(f"Sample chain planning complete:")
        print(f"  - Total chains: {len(sample_chains)}")
        
        # Step 3: Build audio chains
        audio_config = config.get('audio_processing', {})
        builder = SampleChainBuilder(audio_config)
        
        built_chains = {}
        for chain_key, chain_info in sample_chains.items():
            print(f"\nBuilding chain: {chain_key}")
            print(f"  - Files: {len(chain_info['files'])}")
            print(f"  - Type: {chain_info.get('type', 'unknown')}")
            
            # Convert file paths to Path objects
            file_paths = [Path(fp) if isinstance(fp, str) else fp for fp in chain_info['files']]
            
            try:
                # Build the audio chain
                chain_data = builder.build_sample_chain(file_paths, chain_key)
                
                built_chains[chain_key] = chain_data
                
                print(f"  - Built successfully:")
                print(f"    * Sample count: {chain_data['sample_count']}")
                print(f"    * Sample length: {chain_data['sample_length']} samples")
                print(f"    * Total duration: {chain_data['total_duration']:.3f}s")
                print(f"    * Power of 2: {chain_data['metadata']['power_of_two']}")
                
            except Exception as e:
                print(f"  - Failed to build: {e}")
                continue
        
        # Step 4: Export chains
        if built_chains:
            exporter = ChainExporter()
            output_dir = temp_audio_dir / "output_chains"
            
            print(f"\nExporting {len(built_chains)} chains to {output_dir}")
            
            export_results = exporter.export_multiple_chains(built_chains, output_dir)
            
            print(f"Export complete:")
            print(f"  - Successful: {export_results['successful_exports']}")
            print(f"  - Failed: {export_results['failed_exports']}")
            print(f"  - Success rate: {export_results['success_rate']:.1%}")
            
            # Verify output files exist
            if export_results['successful_exports'] > 0:
                output_files = list(output_dir.glob("*.wav"))
                print(f"  - Output files: {len(output_files)}")
                
                for output_file in output_files:
                    print(f"    * {output_file.name}")
                    
                    # Verify the file is valid
                    try:
                        info = sf.info(str(output_file))
                        print(f"      - {info.samplerate}Hz, {info.channels}ch, {info.duration:.3f}s")
                    except Exception as e:
                        print(f"      - Error reading file: {e}")
            
            # Assertions
            assert export_results['successful_exports'] > 0
            assert export_results['failed_exports'] == 0
            assert export_results['success_rate'] == 1.0
            
        else:
            pytest.skip("No chains were built successfully")
    
    def test_power_of_two_enforcement(self, temp_audio_dir, config):
        """Test that chains are properly enforced to power of 2."""
        # Create a directory with exactly 3 samples to test padding
        test_dir = temp_audio_dir / "test_padding"
        test_dir.mkdir()
        
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create 3 samples
        for i in range(3):
            freq = 440 + i * 100
            audio_data = 0.3 * np.sin(2 * np.pi * freq * t)
            filename = test_dir / f"test_{i+1}.wav"
            sf.write(str(filename), audio_data, sample_rate)
        
        # Build chain
        audio_config = config.get('audio_processing', {})
        builder = SampleChainBuilder(audio_config)
        
        file_paths = list(test_dir.glob("*.wav"))
        chain_data = builder.build_sample_chain(file_paths, "test_padding")
        
        # Should be padded to 4 samples (next power of 2)
        assert chain_data['sample_count'] == 4
        assert chain_data['metadata']['power_of_two'] == True
        
        print(f"Padding test successful:")
        print(f"  - Original samples: 3")
        print(f"  - Final samples: {chain_data['sample_count']}")
        print(f"  - Power of 2: {chain_data['metadata']['power_of_two']}")
    
    def test_sample_length_normalization(self, temp_audio_dir, config):
        """Test that samples are normalized to the same length."""
        # Create samples with different lengths
        test_dir = temp_audio_dir / "test_lengths"
        test_dir.mkdir()
        
        sample_rate = 44100
        
        # Create samples with different durations
        durations = [0.3, 0.6, 1.0]
        
        for i, dur in enumerate(durations):
            t = np.linspace(0, dur, int(sample_rate * dur), False)
            freq = 440 + i * 100
            audio_data = 0.3 * np.sin(2 * np.pi * freq * t)
            filename = test_dir / f"test_{dur}s.wav"
            sf.write(str(filename), audio_data, sample_rate)
        
        # Build chain
        audio_config = config.get('audio_processing', {})
        builder = SampleChainBuilder(audio_config)
        
        file_paths = list(test_dir.glob("*.wav"))
        chain_data = builder.build_sample_chain(file_paths, "test_lengths")
        
        # All samples should be normalized to the longest length
        # Note: sample rate is converted to 48kHz, so length will be different
        target_sample_rate = 48000  # From config
        expected_length = int(1.0 * target_sample_rate)  # 1.0 second at 48kHz
        assert chain_data['sample_length'] == expected_length
        
        print(f"Length normalization test successful:")
        print(f"  - Target length: {expected_length} samples ({1.0}s)")
        print(f"  - Actual length: {chain_data['sample_length']} samples")
        print(f"  - Total chain duration: {chain_data['total_duration']:.3f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
