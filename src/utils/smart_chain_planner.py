"""
Smart Chain Planner

Implements intelligent sample chain planning with hi-hat interleaving and
directory-based grouping.
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import numpy as np
from .sample_chain_config import SampleChainConfig

class SmartChainPlanner:
    """
    Plans sample chains intelligently based on file types and directory structure.
    """
    
    def __init__(self, config: SampleChainConfig):
        """
        Initialize the smart chain planner.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.max_samples_per_chain = config.max_samples_per_chain
    
    def plan_smart_chains(self, audio_files: List[Path]) -> Dict[str, Dict[str, Any]]:
        """
        Plan sample chains from audio files.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Dictionary of planned chains
        """
        print("📏 Analyzing sample durations...")
        
        # Analyze sample durations
        audio_info = self.config.analyze_sample_durations(audio_files)
        
        # Separate hi-hat and regular files
        hihat_files = []
        regular_files = []
        
        for file_path in audio_files:
            is_hihat, hihat_type = self.config.is_hihat_file(file_path)
            if is_hihat:
                hihat_files.append((file_path, hihat_type))
            else:
                regular_files.append(file_path)
        
        # Plan hi-hat chains
        hihat_chains = self._create_combined_hihat_chains(hihat_files, audio_info)
        
        # Plan regular chains
        regular_chains = self._create_regular_chains(regular_files, audio_info)
        
        # Combine all chains
        all_chains = {}
        all_chains.update(hihat_chains)
        all_chains.update(regular_chains)
        
        return all_chains
    
    def _create_combined_hihat_chains(self, hihat_files: List[Tuple[Path, str]], 
                                    audio_info: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """
        Create hi-hat chains with closed/open interleaving.
        
        Args:
            hihat_files: List of (file_path, hihat_type) tuples
            audio_info: Dictionary of audio file info
            
        Returns:
            Dictionary of hi-hat chains
        """
        if not hihat_files:
            return {}
        
        # Group hi-hats by base name
        hihat_groups = defaultdict(lambda: {'closed': [], 'open': []})
        
        for file_path, hihat_type in hihat_files:
            base_name = self.config.extract_base_name(file_path)
            hihat_groups[base_name][hihat_type].append(file_path)
        
        # Create chains from hi-hat groups
        chains = {}
        chain_counter = 1
        
        # Sort groups by name for consistent ordering
        sorted_groups = sorted(hihat_groups.items())
        
        current_chain_files = []
        current_chain_metadata = {
            'closed_count': 0,
            'open_count': 0,
            'hat_names': [],
            'total_files': 0
        }
        
        for base_name, hihat_types in sorted_groups:
            closed_files = sorted(hihat_types['closed'])
            open_files = sorted(hihat_types['open'])
            
            # Add all files from this hi-hat name to the current chain
            all_files = closed_files + open_files
            
            # Check if adding these files would exceed the limit
            if len(current_chain_files) + len(all_files) > self.max_samples_per_chain:
                # Current chain is full, save it and start a new one
                if current_chain_files:
                    chain_name = f"hats_{chain_counter}"
                    chains[chain_name] = self._create_chain_from_files(
                        current_chain_files, audio_info, chain_name, current_chain_metadata
                    )
                    chain_counter += 1
                
                # Start new chain
                current_chain_files = all_files
                current_chain_metadata = {
                    'closed_count': len(closed_files),
                    'open_count': len(open_files),
                    'hat_names': [base_name],
                    'total_files': len(all_files)
                }
            else:
                # Add to current chain
                current_chain_files.extend(all_files)
                current_chain_metadata['closed_count'] += len(closed_files)
                current_chain_metadata['open_count'] += len(open_files)
                current_chain_metadata['hat_names'].append(base_name)
                current_chain_metadata['total_files'] += len(all_files)
        
        # Save the last chain if it has files
        if current_chain_files:
            chain_name = f"hats_{chain_counter}"
            chains[chain_name] = self._create_chain_from_files(
                current_chain_files, audio_info, chain_name, current_chain_metadata
            )
        
        return chains
    
    def _create_regular_chains(self, regular_files: List[Path], 
                              audio_info: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """
        Create regular chains based on directory structure.
        
        Args:
            regular_files: List of regular audio file paths
            audio_info: Dictionary of audio file info
            
        Returns:
            Dictionary of regular chains
        """
        if not regular_files:
            return {}
        
        # Group files by directory structure
        directory_groups = defaultdict(list)
        
        for file_path in regular_files:
            # Use the parent directory as the group key
            parent_dir = file_path.parent
            if parent_dir.name:  # Not root directory
                group_key = f"{parent_dir.parent.name}/{parent_dir.name}" if parent_dir.parent.name else parent_dir.name
            else:
                group_key = "root"
            
            directory_groups[group_key].append(file_path)
        
        # Create chains from directory groups
        chains = {}
        
        for group_key, files in directory_groups.items():
            # Sort files for consistent ordering
            sorted_files = sorted(files)
            
            # Split into chains if needed
            if len(sorted_files) <= self.max_samples_per_chain:
                # Single chain
                chain_name = group_key
                chains[chain_name] = self._create_chain_from_files(
                    sorted_files, audio_info, chain_name, {'total_files': len(sorted_files)}
                )
            else:
                # Split into multiple chains
                num_chains = (len(sorted_files) + self.max_samples_per_chain - 1) // self.max_samples_per_chain
                
                for i in range(num_chains):
                    start_idx = i * self.max_samples_per_chain
                    end_idx = min(start_idx + self.max_samples_per_chain, len(sorted_files))
                    chain_files = sorted_files[start_idx:end_idx]
                    
                    chain_name = f"{group_key}_{i + 1}"
                    chains[chain_name] = self._create_chain_from_files(
                        chain_files, audio_info, chain_name, {'total_files': len(chain_files)}
                    )
        
        return chains
    
    def _create_chain_from_files(self, files: List[Path], 
                                audio_info: Dict[str, Dict[str, float]], 
                                chain_name: str, 
                                additional_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a chain data structure from a list of files.
        
        Args:
            files: List of file paths
            audio_info: Dictionary of audio file info
            chain_name: Name of the chain
            additional_metadata: Additional metadata to include
            
        Returns:
            Chain data dictionary
        """
        # Get audio info for these files
        chain_audio_info = {str(f): audio_info[str(f)] for f in files if str(f) in audio_info}
        
        # Calculate metadata
        total_duration = sum(info['duration'] for info in chain_audio_info.values())
        estimated_size_mb = self.config.get_estimated_file_size_mb_from_audio_info(chain_audio_info)
        
        # Create metadata
        metadata = {
            'type': 'hihat' if chain_name.startswith('hats') else 'regular',
            'sample_count': len(files),
            'estimated_duration_seconds': total_duration,
            'estimated_file_size_mb': estimated_size_mb,
            'chain_number': 1,
            'max_samples_per_chain': self.max_samples_per_chain,
            **additional_metadata
        }
        
        # Add hi-hat specific metadata
        if chain_name.startswith('hats'):
            metadata.update({
                'interleaved_sequence': self._create_interleaved_sequence(files)
            })
        
        return {
            'files': files,
            'metadata': metadata
        }
    
    def _create_interleaved_sequence(self, files: List[Path]) -> List[str]:
        """
        Create an interleaved sequence for hi-hat files.
        
        Args:
            files: List of hi-hat file paths
            
        Returns:
            List of file paths in interleaved order
        """
        # Group files by base name and type
        file_groups = defaultdict(lambda: {'closed': [], 'open': []})
        
        for file_path in files:
            is_hihat, hihat_type = self.config.is_hihat_file(file_path)
            if is_hihat:
                base_name = self.config.extract_base_name(file_path)
                file_groups[base_name][hihat_type].append(file_path)
        
        # Create interleaved sequence
        interleaved = []
        
        for base_name in sorted(file_groups.keys()):
            group = file_groups[base_name]
            closed_files = sorted(group['closed'])
            open_files = sorted(group['open'])
            
            # Add closed files first, then open files
            interleaved.extend(closed_files)
            interleaved.extend(open_files)
        
        return [str(f) for f in interleaved] 
