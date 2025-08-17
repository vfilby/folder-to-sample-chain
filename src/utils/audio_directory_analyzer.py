"""
Audio Directory Analyzer for NI Sample Chainer

This module provides utilities for analyzing and processing real-world
audio directory structures, organizing files by category, and planning
sample chain generation.
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import re
from collections import defaultdict

class AudioDirectoryAnalyzer:
    """Analyze and organize audio directory structures."""
    
    def __init__(self, root_directory: Path):
        """Initialize the analyzer with a root directory."""
        self.root_directory = Path(root_directory)
        self.audio_extensions = {'.wav', '.WAV', '.flac', '.FLAC', '.aiff', '.AIFF'}
        self.audio_files = []
        self.directory_structure = {}
        self.file_categories = defaultdict(list)
        
        # Common audio category patterns
        self.category_patterns = {
            'drum': [
                r'\b(kick|snare|hihat|clap|tom|cymbal|percussion|shaker|mallet|drum)\b',
                r'\b(ClosedHH|OpenHH|ClsdHH|Ride|Cowbell|Clave|Conga)\b'
            ],
            'bass': [
                r'\b(bass|bontempo|cohesion|dirac|error.?code|fallout|gogettue|ruebycon|scalar|shoveler|totalistic)\b'
            ],
            'lead': [
                r'\b(lead|anaerobic|beirut|cassata|circularism|delta.?curve|dweller|echnatone|ethifier|harmotron|schmoof)\b'
            ],
            'loop': [
                r'\b(loop|construction|chord\[\d+\]|drums\[\d+\]|full\[\d+\]|bass\[\d+\]|kick\[\d+\]|perc\[\d+\]|hihats\[\d+\]|shaker\[\d+\]|snare\[\d+\]|combo\[\d+\]|sfx\[\d+\]|glitch\[\d+\]|ride\[\d+\]|rim\[\d+\]|stab\[\d+\]|tom\[\d+\]|synth\[\d+\]|conga\[\d+\])\b'
            ],
            'one_shot': [
                r'\b(ambience|analog.?fx|blip.?&.?blop|buzz|chord|glitch|impact|noise|sweep.?&.?swell|synth.?note|dive|rise|squelch|whoop|wow|bleep|resosynth)\b'
            ]
        }
        
        # Initialize analysis
        self._analyze_directory()
    
    def _analyze_directory(self):
        """Analyze the directory structure and categorize files."""
        if not self.root_directory.exists():
            raise ValueError(f"Root directory {self.root_directory} does not exist")
        
        # Find all audio files
        self.audio_files = []
        for root, dirs, files in os.walk(self.root_directory):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if file_path.suffix.lower() in {ext.lower() for ext in self.audio_extensions}:
                    self.audio_files.append(file_path)
        
        # Build directory structure
        self._build_directory_structure()
        
        # Categorize files
        self._categorize_files()
    
    def _build_directory_structure(self):
        """Build a hierarchical representation of the directory structure."""
        self.directory_structure = {}
        
        for file_path in self.audio_files:
            relative_path = file_path.relative_to(self.root_directory)
            path_parts = relative_path.parts
            
            current_level = self.directory_structure
            for i, part in enumerate(path_parts[:-1]):
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            # Add file to the current level
            if path_parts[-1] not in current_level:
                current_level[path_parts[-1]] = []
            if isinstance(current_level[path_parts[-1]], list):
                current_level[path_parts[-1]].append(str(file_path))
    
    def _categorize_files(self):
        """Categorize audio files based on naming patterns and directory structure."""
        for file_path in self.audio_files:
            filename = file_path.name.lower()
            relative_path = str(file_path.relative_to(self.root_directory)).lower()
            
            # Determine category based on patterns
            category = self._determine_file_category(filename, relative_path)
            
            if category:
                self.file_categories[category].append(str(file_path))
    
    def _determine_file_category(self, filename: str, relative_path: str) -> Optional[str]:
        """Determine the category of an audio file based on its name and path."""
        # Check each category pattern
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE) or re.search(pattern, relative_path, re.IGNORECASE):
                    return category
        
        # Fallback: determine by directory structure
        if 'drum' in relative_path or any(drum_term in relative_path for drum_term in ['kick', 'snare', 'hihat', 'clap', 'tom', 'cymbal', 'percussion', 'shaker', 'mallet']):
            return 'drum'
        elif 'bass' in relative_path:
            return 'bass'
        elif 'lead' in relative_path:
            return 'lead'
        elif 'loop' in relative_path or 'construction' in relative_path:
            return 'loop'
        elif 'one.?shot' in relative_path or any(shot_term in relative_path for shot_term in ['ambience', 'analog', 'blip', 'buzz', 'chord', 'glitch', 'impact', 'noise', 'sweep', 'synth']):
            return 'one_shot'
        
        return None
    
    def get_directory_structure(self) -> Dict[str, Any]:
        """Get the analyzed directory structure."""
        return self.directory_structure
    
    def get_file_categories(self) -> Dict[str, List[str]]:
        """Get files organized by category."""
        return dict(self.file_categories)
    
    def get_audio_files(self) -> List[Path]:
        """Get all discovered audio files."""
        return self.audio_files
    
    def get_files_by_category(self, category: str) -> List[str]:
        """Get all files in a specific category."""
        return self.file_categories.get(category, [])
    
    def get_category_summary(self) -> Dict[str, int]:
        """Get a summary of file counts by category."""
        return {category: len(files) for category, files in self.file_categories.items()}
    
    def get_directory_depth_analysis(self) -> Dict[str, int]:
        """Analyze the depth of each main directory category."""
        depth_analysis = {}
        
        for category, contents in self.directory_structure.items():
            depth = self._calculate_directory_depth(contents)
            depth_analysis[category] = depth
        
        return depth_analysis
    
    def _calculate_directory_depth(self, contents: Any, current_depth: int = 1) -> int:
        """Calculate the maximum depth of a directory structure."""
        if isinstance(contents, dict):
            max_depth = current_depth
            for value in contents.values():
                depth = self._calculate_directory_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            return max_depth
        elif isinstance(contents, list):
            return current_depth
        else:
            return current_depth
    
    def plan_sample_chains(self, max_samples_per_chain: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Plan sample chains based on the analyzed directory structure."""
        sample_chains = {}
        
        # Plan drum kit chains
        drum_files = self.get_files_by_category('drum')
        if drum_files:
            drum_chains = self._plan_drum_chains(drum_files, max_samples_per_chain)
            sample_chains.update(drum_chains)
        
        # Plan instrument chains
        bass_files = self.get_files_by_category('bass')
        if bass_files:
            bass_chains = self._plan_instrument_chains(bass_files, 'bass', max_samples_per_chain)
            sample_chains.update(bass_chains)
        
        lead_files = self.get_files_by_category('lead')
        if lead_files:
            lead_chains = self._plan_instrument_chains(lead_files, 'lead', max_samples_per_chain)
            sample_chains.update(lead_chains)
        
        # Plan loop chains
        loop_files = self.get_files_by_category('loop')
        if loop_files:
            loop_chains = self._plan_loop_chains(loop_files, max_samples_per_chain)
            sample_chains.update(loop_chains)
        
        return sample_chains
    
    def _plan_drum_chains(self, drum_files: List[str], max_samples: int) -> Dict[str, Dict[str, List[str]]]:
        """Plan drum kit sample chains."""
        drum_chains = {}
        
        # Group files by drum type
        drum_types = defaultdict(list)
        for file_path in drum_files:
            filename = Path(file_path).name.lower()
            
            # Determine drum type from filename
            drum_type = self._extract_drum_type(filename)
            if drum_type:
                drum_types[drum_type].append(file_path)
        
        # Create chains for each drum type
        for drum_type, files in drum_types.items():
            if len(files) > 0:
                # Limit samples per chain
                selected_files = files[:max_samples]
                chain_name = f"drum_kit_{drum_type}"
                drum_chains[chain_name] = {
                    drum_type: selected_files,
                    'metadata': {
                        'type': 'drum_kit',
                        'drum_type': drum_type,
                        'sample_count': len(selected_files),
                        'source_files': selected_files
                    }
                }
        
        return drum_chains
    
    def _extract_drum_type(self, filename: str) -> Optional[str]:
        """Extract drum type from filename."""
        drum_patterns = {
            'kick': r'\bkick\b',
            'snare': r'\bsnare\b',
            'hihat': r'\b(hihat|closedhh|openhh|clsdhh)\b',
            'clap': r'\bclap\b',
            'tom': r'\btom\b',
            'cymbal': r'\b(cymbal|ride)\b',
            'percussion': r'\bperc\b',
            'shaker': r'\bshaker\b',
            'mallet': r'\bmallet\b'
        }
        
        for drum_type, pattern in drum_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return drum_type
        
        return None
    
    def _plan_instrument_chains(self, instrument_files: List[str], instrument_type: str, max_samples: int) -> Dict[str, Dict[str, List[str]]]:
        """Plan instrument sample chains."""
        instrument_chains = {}
        
        # Group files by instrument family
        instrument_families = defaultdict(list)
        for file_path in instrument_files:
            filename = Path(file_path).name
            family = self._extract_instrument_family(filename)
            if family:
                instrument_families[family].append(file_path)
        
        # Create chains for each instrument family
        for family, files in instrument_families.items():
            if len(files) > 0:
                selected_files = files[:max_samples]
                chain_name = f"{instrument_type}_{family}"
                instrument_chains[chain_name] = {
                    family: selected_files,
                    'metadata': {
                        'type': instrument_type,
                        'family': family,
                        'sample_count': len(selected_files),
                        'source_files': selected_files
                    }
                }
        
        return instrument_chains
    
    def _extract_instrument_family(self, filename: str) -> Optional[str]:
        """Extract instrument family from filename."""
        # Extract the first word before any numbers or special characters
        match = re.match(r'^([A-Za-z]+)', filename)
        if match:
            return match.group(1).lower()
        return None
    
    def _plan_loop_chains(self, loop_files: List[str], max_samples: int) -> Dict[str, Dict[str, List[str]]]:
        """Plan loop sample chains."""
        loop_chains = {}
        
        # Group files by loop style/construction kit
        loop_styles = defaultdict(list)
        for file_path in loop_files:
            filename = Path(file_path).name
            style = self._extract_loop_style(filename)
            if style:
                loop_styles[style].append(file_path)
        
        # Create chains for each loop style
        for style, files in loop_styles.items():
            if len(files) > 0:
                selected_files = files[:max_samples]
                chain_name = f"loop_{style}"
                loop_chains[chain_name] = {
                    style: selected_files,
                    'metadata': {
                        'type': 'loop',
                        'style': style,
                        'sample_count': len(selected_files),
                        'source_files': selected_files
                    }
                }
        
        return loop_chains
    
    def _extract_loop_style(self, filename: str) -> Optional[str]:
        """Extract loop style from filename."""
        # Look for construction kit names in brackets or after specific patterns
        match = re.search(r'\[121\]\s+([A-Za-z]+)', filename)
        if match:
            return match.group(1).lower()
        
        # Fallback: extract first word
        match = re.match(r'^([A-Za-z]+)', filename)
        if match:
            return match.group(1).lower()
        
        return None
    
    def generate_export_structure(self, sample_chains: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Generate the export structure for sample chains."""
        export_structure = {
            'metadata': {
                'source_directory': str(self.root_directory),
                'total_files': len(self.audio_files),
                'categories': self.get_category_summary(),
                'generated_at': str(Path.cwd()),
                'version': '1.0.0'
            },
            'sample_chains': sample_chains,
            'export_settings': {
                'format': 'wav',
                'sample_rate': 44100,
                'bit_depth': 16,
                'channels': 'stereo'
            }
        }
        
        return export_structure

def analyze_audio_directory(directory_path: str) -> AudioDirectoryAnalyzer:
    """Convenience function to analyze an audio directory."""
    return AudioDirectoryAnalyzer(Path(directory_path))

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
        analyzer = analyze_audio_directory(directory_path)
        
        print(f"Audio Directory Analysis: {directory_path}")
        print("=" * 50)
        
        print(f"Total audio files: {len(analyzer.get_audio_files())}")
        print(f"Categories: {analyzer.get_category_summary()}")
        print(f"Directory depth analysis: {analyzer.get_directory_depth_analysis()}")
        
        # Plan sample chains
        sample_chains = analyzer.plan_sample_chains()
        print(f"Planned sample chains: {len(sample_chains)}")
        
        # Generate export structure
        export_structure = analyzer.generate_export_structure(sample_chains)
        print("Export structure generated successfully")
        
    else:
        print("Usage: python audio_directory_analyzer.py <directory_path>")



