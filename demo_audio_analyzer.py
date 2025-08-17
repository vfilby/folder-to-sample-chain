#!/usr/bin/env python3
"""
Demo Script for Audio Directory Analyzer

This script demonstrates how to use the AudioDirectoryAnalyzer
to process real-world audio sample library structures.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.audio_directory_analyzer import AudioDirectoryAnalyzer, analyze_audio_directory

def demo_with_sample_structure():
    """Demonstrate the analyzer with a sample directory structure."""
    print("🎵 Audio Directory Analyzer Demo")
    print("=" * 50)
    
    # Create a temporary sample structure for demonstration
    demo_dir = Path("demo_audio_library")
    demo_dir.mkdir(exist_ok=True)
    
    try:
        # Create sample structure
        _create_demo_structure(demo_dir)
        
        # Analyze the directory
        print(f"📁 Analyzing directory: {demo_dir}")
        analyzer = AudioDirectoryAnalyzer(demo_dir)
        
        # Display results
        _display_analysis_results(analyzer)
        
        # Plan sample chains
        _display_sample_chains(analyzer)
        
        # Generate export structure
        _display_export_structure(analyzer)
        
    finally:
        # Clean up
        import shutil
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
            print(f"\n🧹 Cleaned up demo directory: {demo_dir}")

def _create_demo_structure(demo_dir: Path):
    """Create a demo directory structure."""
    # Create main categories
    (demo_dir / 'Drums').mkdir()
    (demo_dir / 'Instruments').mkdir()
    (demo_dir / 'Loops').mkdir()
    (demo_dir / 'One Shots').mkdir()
    
    # Create drum subcategories
    (demo_dir / 'Drums' / 'Kick').mkdir()
    (demo_dir / 'Drums' / 'Snare').mkdir()
    (demo_dir / 'Drums' / 'Hihat').mkdir()
    
    # Create instrument subcategories
    (demo_dir / 'Instruments' / 'Bass').mkdir()
    (demo_dir / 'Instruments' / 'Lead').mkdir()
    (demo_dir / 'Instruments' / 'Bass' / 'Bontempo').mkdir()
    
    # Create loop subcategories
    (demo_dir / 'Loops' / 'Construction').mkdir()
    (demo_dir / 'Loops' / 'Construction' / 'Aberlour').mkdir()
    
    # Create one shot subcategories
    (demo_dir / 'One Shots' / 'Ambience').mkdir()
    (demo_dir / 'One Shots' / 'Analog FX').mkdir()
    
    # Create sample audio files
    sample_files = [
        'Drums/Kick/Kick Aberlour 1.wav',
        'Drums/Kick/Kick Aberlour 2.wav',
        'Drums/Snare/Snare Aberlour 1.wav',
        'Drums/Snare/Snare Aberlour 2.wav',
        'Drums/Hihat/ClosedHH Aberlour 1.wav',
        'Drums/Hihat/OpenHH Aberlour.wav',
        'Instruments/Bass/Bontempo/Bontempo A2.wav',
        'Instruments/Bass/Bontempo/Bontempo A3.wav',
        'Loops/Construction/Aberlour/Chord[121] E Aberlour.wav',
        'Loops/Construction/Aberlour/Drums[121] Aberlour 1.wav',
        'One Shots/Ambience/Ambience Transistor 01.wav',
        'One Shots/Analog FX/Dive Berg.wav'
    ]
    
    for file_path in sample_files:
        full_path = demo_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        # Create a simple text file that simulates WAV data
        full_path.write_text(f"# Mock WAV file: {file_path}")

def _display_analysis_results(analyzer: AudioDirectoryAnalyzer):
    """Display the analysis results."""
    print("\n📊 Analysis Results:")
    print("-" * 30)
    
    # File counts
    print(f"Total audio files: {len(analyzer.get_audio_files())}")
    
    # Category summary
    category_summary = analyzer.get_category_summary()
    print(f"File categories: {category_summary}")
    
    # Directory depth analysis
    depth_analysis = analyzer.get_directory_depth_analysis()
    print(f"Directory depths: {depth_analysis}")
    
    # Directory structure
    structure = analyzer.get_directory_structure()
    print(f"\n📁 Directory Structure:")
    _print_directory_structure(structure, indent=2)

def _print_directory_structure(structure: dict, indent: int = 0):
    """Print directory structure in a readable format."""
    for key, value in structure.items():
        print(" " * indent + f"├── {key}")
        if isinstance(value, dict):
            _print_directory_structure(value, indent + 2)
        elif isinstance(value, list):
            for item in value[:3]:  # Show first 3 items
                print(" " * (indent + 2) + f"├── {Path(item).name}")
            if len(value) > 3:
                print(" " * (indent + 2) + f"├── ... and {len(value) - 3} more")

def _display_sample_chains(analyzer: AudioDirectoryAnalyzer):
    """Display planned sample chains."""
    print(f"\n🔗 Sample Chain Planning:")
    print("-" * 30)
    
    sample_chains = analyzer.plan_sample_chains(max_samples_per_chain=5)
    
    for chain_name, chain_data in sample_chains.items():
        print(f"\n📦 {chain_name}:")
        for key, value in chain_data.items():
            if key != 'metadata':
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} samples")
                    for i, sample in enumerate(value[:3]):
                        print(f"    {i+1}. {Path(sample).name}")
                    if len(value) > 3:
                        print(f"    ... and {len(value) - 3} more")
                else:
                    print(f"  {key}: {value}")

def _display_export_structure(analyzer: AudioDirectoryAnalyzer):
    """Display the export structure."""
    print(f"\n📤 Export Structure:")
    print("-" * 30)
    
    sample_chains = analyzer.plan_sample_chains()
    export_structure = analyzer.generate_export_structure(sample_chains)
    
    print(f"Metadata:")
    for key, value in export_structure['metadata'].items():
        if key != 'source_directory':
            print(f"  {key}: {value}")
    
    print(f"\nExport Settings:")
    for key, value in export_structure['export_settings'].items():
        print(f"  {key}: {value}")
    
    print(f"\nSample Chains: {len(export_structure['sample_chains'])} chains planned")

def demo_with_real_directory(directory_path: str):
    """Demonstrate the analyzer with a real directory."""
    print(f"🎵 Analyzing Real Directory: {directory_path}")
    print("=" * 50)
    
    try:
        # Analyze the directory
        analyzer = analyze_audio_directory(directory_path)
        
        # Display results
        _display_analysis_results(analyzer)
        
        # Plan sample chains
        _display_sample_chains(analyzer)
        
        # Generate export structure
        _display_export_structure(analyzer)
        
    except Exception as e:
        print(f"❌ Error analyzing directory: {e}")
        print("Make sure the directory exists and contains audio files.")

def main():
    """Main demo function."""
    if len(sys.argv) > 1:
        # Analyze a real directory
        directory_path = sys.argv[1]
        demo_with_real_directory(directory_path)
    else:
        # Run demo with sample structure
        demo_with_sample_structure()
    
    print(f"\n🎉 Demo completed!")
    print(f"\n💡 Usage:")
    print(f"  python {sys.argv[0]}                    # Run with demo structure")
    print(f"  python {sys.argv[0]} /path/to/audio     # Analyze real directory")

if __name__ == "__main__":
    main()



