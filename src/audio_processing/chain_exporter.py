"""
Chain Exporter

Handles exporting sample chains to disk with proper formatting and metadata.
"""

import soundfile as sf
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from .sample_chain_builder import SampleChainBuilder

logger = logging.getLogger(__name__)


class ChainExporter:
    """
    Exports sample chains to disk with proper formatting and metadata.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the chain exporter.
        
        Args:
            config: Configuration dictionary with export settings
        """
        self.config = config or {}
        self.output_format = self.config.get('output_format', 'wav')
        self.include_metadata = self.config.get('include_metadata', True)
        self.metadata_format = self.config.get('metadata_format', 'json')
        
    def export_chain(self, chain_data: Dict[str, Any], output_path: Path, 
                    filename: Optional[str] = None, root_metadata_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Export a sample chain to disk.
        
        IMPORTANT: This method NEVER modifies the source audio files. It only creates
        new output files from the processed audio data in memory.
        
        Args:
            chain_data: Chain data from SampleChainBuilder
            output_path: Directory to save the chain
            filename: Optional custom filename
            
        Returns:
            Dictionary with export results
        """
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
            
        # Generate filename if not provided
        if not filename:
            filename = self._generate_filename(chain_data)
            
        # Ensure proper extension
        if not filename.endswith(f'.{self.output_format}'):
            filename += f'.{self.output_format}'
            
        # Full output path
        full_output_path = output_path / filename
        
        # Export audio file
        audio_result = self._export_audio_file(chain_data, full_output_path)
        
        # Export metadata if requested
        metadata_result = None
        if self.include_metadata:
            metadata_result = self._export_metadata(chain_data, output_path, filename, root_metadata_dir)
            
        return {
            'success': audio_result['success'],
            'output_path': str(full_output_path),
            'filename': filename,
            'audio_export': audio_result,
            'metadata_export': metadata_result,
            'chain_info': {
                'sample_count': chain_data['metadata']['sample_count'],
                'sample_length': chain_data['chain']['sample_length'],
                'total_duration': chain_data['chain']['total_duration'],
                'sample_rate': chain_data['chain']['metadata']['sample_rate'],
                'bit_depth': chain_data['chain']['metadata']['bit_depth'],
                'channels': chain_data['chain']['metadata']['channels']
            }
        }
    
    def _generate_filename(self, chain_data: Dict[str, Any]) -> str:
        """
        Generate a filename for the chain.
        
        Args:
            chain_data: Chain data
            
        Returns:
            Generated filename
        """
        # Use the name field which contains the group information
        group_key = chain_data.get('name', 'unknown')
        
        # Extract components from group key (e.g., "drums/kick" -> "drums-kick")
        if '/' in group_key:
            group_parts = group_key.split('/')
            if len(group_parts) >= 2:
                category = group_parts[0]
                subcategory = group_parts[1]
                base_name = f"{category}-{subcategory}"
            else:
                base_name = group_key.replace('/', '-')
        else:
            base_name = group_key
            
        # Get sample count and duration from metadata
        metadata = chain_data.get('metadata', {})
        sample_count = metadata.get('sample_count', 0)
        sample_duration = metadata.get('estimated_duration_seconds', 0)
        
        filename = f"{base_name}-{sample_count}-{sample_duration:.3f}s"
        return filename
    
    def _export_audio_file(self, chain_data: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
        """
        Export the audio data to a file.
        
        Args:
            chain_data: Chain data
            output_path: Output file path
            
        Returns:
            Export result dictionary
        """
        try:
            # The audio data is in chain_data['chain']['audio_data']
            audio_data = chain_data['chain']['audio_data']
            metadata = chain_data['chain']['metadata']
            
            # Determine soundfile subtype based on bit depth
            if metadata['bit_depth'] == 16:
                subtype = 'PCM_16'
            elif metadata['bit_depth'] == 24:
                subtype = 'PCM_24'
            elif metadata['bit_depth'] == 32:
                subtype = 'FLOAT'
            else:
                subtype = 'PCM_16'  # Default
                
            # Write audio file
            sf.write(
                str(output_path),
                audio_data,
                metadata['sample_rate'],
                subtype=subtype
            )
            
            logger.info(f"Exported audio chain to {output_path}")
            
            return {
                'success': True,
                'file_size': output_path.stat().st_size,
                'subtype': subtype
            }
            
        except Exception as e:
            logger.error(f"Failed to export audio file {output_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_metadata(self, chain_data: Dict[str, Any], output_dir: Path, 
                        base_filename: str, root_metadata_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Export metadata for the chain.
        
        Args:
            chain_data: Chain data
            output_dir: Output directory
            base_filename: Base filename (without extension)
            
        Returns:
            Metadata export result
        """
        try:
            metadata = chain_data['metadata']
            
            if self.metadata_format == 'json':
                # Only export to root metadata folder if specified
                if root_metadata_dir:
                    root_metadata_dir.mkdir(exist_ok=True)
                    metadata_filename = base_filename.replace(f'.{self.output_format}', '.json')
                    root_metadata_path = root_metadata_dir / metadata_filename
                    
                    # Convert numpy types to native Python types for JSON serialization
                    json_metadata = self._prepare_metadata_for_json(metadata)
                    
                    with open(root_metadata_path, 'w') as f:
                        json.dump(json_metadata, f, indent=2)
                        
                    logger.info(f"Exported metadata to root folder: {root_metadata_path}")
                    
                    return {
                        'success': True,
                        'format': 'json',
                        'path': str(root_metadata_path)
                    }
                else:
                    # No metadata export if no root metadata directory specified
                    return {
                        'success': True,
                        'format': 'json',
                        'path': None
                    }
                
            else:
                logger.warning(f"Unsupported metadata format: {self.metadata_format}")
                return {
                    'success': False,
                    'error': f"Unsupported metadata format: {self.metadata_format}"
                }
                
        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_metadata_for_json(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare metadata for JSON serialization.
        
        Args:
            metadata: Raw metadata
            
        Returns:
            JSON-serializable metadata
        """
        json_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, (int, float, str, bool, type(None))):
                json_metadata[key] = value
            elif isinstance(value, list):
                # Convert list items
                json_metadata[key] = [
                    str(item) if hasattr(item, '__str__') else item 
                    for item in value
                ]
            else:
                # Convert other types to string
                json_metadata[key] = str(value)
                
        return json_metadata
    
    def export_multiple_chains(self, chains: Dict[str, Dict[str, Any]], 
                              output_dir: Path) -> Dict[str, Any]:
        """
        Export multiple chains to disk.
        
        Args:
            chains: Dictionary of chains to export
            output_dir: Output directory
            
        Returns:
            Export results summary
        """
        results = {}
        total_chains = len(chains)
        successful_exports = 0
        failed_exports = 0
        
        for chain_key, chain_data in chains.items():
            try:
                # Generate filename from chain data
                filename = self._generate_filename(chain_data)
                
                # Export the chain
                result = self.export_chain(chain_data, output_dir, filename)
                
                if result['success']:
                    successful_exports += 1
                    logger.info(f"Successfully exported {chain_key}")
                else:
                    failed_exports += 1
                    logger.error(f"Failed to export {chain_key}")
                    
                results[chain_key] = result
                
            except Exception as e:
                failed_exports += 1
                logger.error(f"Exception during export of {chain_key}: {e}")
                results[chain_key] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Summary
        summary = {
            'total_chains': total_chains,
            'successful_exports': successful_exports,
            'failed_exports': failed_exports,
            'success_rate': successful_exports / total_chains if total_chains > 0 else 0,
            'results': results
        }
        
        logger.info(f"Export complete: {successful_exports}/{total_chains} chains exported successfully")
        return summary
