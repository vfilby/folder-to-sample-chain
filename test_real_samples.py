#!/usr/bin/env python3
"""
Test script for processing real audio samples from sample_data/input/

This script demonstrates the complete pipeline with your actual audio files.
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.audio_directory_analyzer import AudioDirectoryAnalyzer
from utils.smart_chain_planner import SmartChainPlanner
from audio_processing.sample_chain_builder import SampleChainBuilder
from audio_processing.chain_exporter import ChainExporter
from utils.config import ConfigManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Process real audio samples from sample_data/input/"""
    
    # Paths
    input_dir = Path('sample_data/input')
    output_dir = Path('sample_data/output')
    
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} not found!")
        print("Please add your audio files to sample_data/input/ first.")
        return
    
    print("🎵 NI Sample Chainer - Real Sample Processing Test")
    print("=" * 60)
    print(f"Input directory: {input_dir.absolute()}")
    print(f"Output directory: {output_dir.absolute()}")
    print()
    
    # Step 1: Analyze the audio directory
    print("📁 Step 1: Analyzing audio directory structure...")
    analyzer = AudioDirectoryAnalyzer(input_dir)
    
    total_files = len(analyzer.get_audio_files())
    categories = analyzer.get_category_summary()
    
    print(f"✅ Found {total_files} audio files")
    print(f"📊 Categories: {categories}")
    print()
    
    # Step 2: Plan sample chains
    print("🎯 Step 2: Planning sample chains...")
    planner = SmartChainPlanner()
    sample_chains = planner.plan_smart_chains(analyzer.get_audio_files())
    
    print(f"✅ Planned {len(sample_chains)} sample chains")
    print()
    
    # Show chain details
    for chain_key, chain_info in sample_chains.items():
        file_count = len(chain_info['files'])
        chain_type = chain_info.get('type', 'unknown')
        print(f"  🔗 {chain_key}: {file_count} files ({chain_type})")
        
        # Show first few files
        for i, file_path in enumerate(chain_info['files'][:3]):
            filename = Path(file_path).name
            print(f"    - {filename}")
        if len(chain_info['files']) > 3:
            print(f"    ... and {len(chain_info['files']) - 3} more")
        print()
    
    # Step 3: Build audio chains
    print("🔨 Step 3: Building audio chains...")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config(Path('config.yaml'))
    audio_config = config.get('audio_processing', {})
    
    builder = SampleChainBuilder(audio_config)
    
    built_chains = {}
    for chain_key, chain_info in sample_chains.items():
        print(f"  🔨 Building: {chain_key}")
        
        # Convert file paths to Path objects
        file_paths = [Path(fp) if isinstance(fp, str) else fp for fp in chain_info['files']]
        
        try:
            # Build the audio chain
            chain_data = builder.build_sample_chain(file_paths, chain_key)
            
            built_chains[chain_key] = chain_data
            
            print(f"    ✅ Success: {chain_data['sample_count']} samples, "
                  f"{chain_data['total_duration']:.3f}s, "
                  f"Power of 2: {chain_data['metadata']['power_of_two']}")
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            continue
    
    if not built_chains:
        print("❌ No chains were built successfully!")
        return
    
    print(f"\n✅ Successfully built {len(built_chains)} audio chains")
    
    # Step 4: Export chains
    print(f"\n💾 Step 4: Exporting chains to {output_dir}...")
    
    exporter = ChainExporter()
    export_results = exporter.export_multiple_chains(built_chains, output_dir)
    
    print(f"✅ Export complete:")
    print(f"   - Successful: {export_results['successful_exports']}")
    print(f"   - Failed: {export_results['failed_exports']}")
    print(f"   - Success rate: {export_results['success_rate']:.1%}")
    
    # Show output files
    if export_results['successful_exports'] > 0:
        print(f"\n📁 Generated files:")
        output_files = list(output_dir.glob("*.wav"))
        
        for output_file in output_files:
            file_size = output_file.stat().st_size / 1024  # KB
            print(f"   - {output_file.name} ({file_size:.1f} KB)")
            
            # Show metadata if available
            metadata_file = output_file.with_suffix('.json')
            if metadata_file.exists():
                print(f"     📄 Metadata: {metadata_file.name}")
    
    print(f"\n🎉 Processing complete! Check {output_dir.absolute()} for your sample chains.")
    print("\n💡 Tip: These chains are ready to load into your Digitakt 2!")


if __name__ == '__main__':
    main()

