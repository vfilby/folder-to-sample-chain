# NI Sample Chainer - Project Specification

## Project Overview
The NI Sample Chainer is a Python-based audio processing tool designed to create evenly spaced sample chains from local WAV files, specifically optimized for use with the Elektron Digitakt 2 sampler.

## Core Functionality

### 1. Audio Input Processing
- **Supported Formats**: WAV files (primary), with potential for MP3/AIFF support
- **Input Validation**: File integrity checks, format verification, metadata extraction
- **Batch Processing**: Process entire directories of audio files
- **Error Handling**: Graceful handling of corrupted or unsupported files

### 2. Sample Chain Generation
- **Evenly Spaced Sample Chains**: Combine multiple audio samples into single files for slicing
- **Chain Structure Rules**:
  - **Power of Two Requirement**: All chains must have a power of 2 samples (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
  - **Padding Strategy**: Unused slots filled by repeating the last sample
  - **Equal Sample Lengths**: All samples in a chain must be the same length
  - **Length Determination**: Use the longest sample in the chain as the target length
  - **Silence Padding**: Pad shorter samples with silence to match the longest sample
- **Audio Format Requirements**:
  - **Output Format**: 16-bit, 48kHz, Stereo (configurable to mono)
  - **Sample Rate Conversion**: Convert all inputs to 48kHz
  - **Bit Depth Conversion**: Convert all inputs to 16-bit
  - **Channel Handling**: Convert all inputs to stereo (unless configured for mono)
- **Quality Preservation**: Maintain original audio fidelity during conversions
- **Metadata Generation**: Create sample information files with timing data

### 3. Digitakt 2 Export
- **Format Compatibility**: Export in formats directly usable by Digitakt 2
- **Naming Convention**: Clear, descriptive names compatible with device file system
- **Organization**: Logical folder structure for easy navigation
- **Size Optimization**: Respect device limitations and optimize file sizes

## Technical Requirements

### Audio Processing
- **Input Support**: 
  - **Sample Rates**: 44.1kHz, 48kHz, 96kHz, 192kHz
  - **Bit Depths**: 16-bit, 24-bit, 32-bit float
  - **Channels**: Mono and stereo files
- **Output Requirements**:
  - **Sample Rate**: 48kHz (configurable)
  - **Bit Depth**: 16-bit (configurable)
  - **Channels**: Stereo (configurable to mono)
- **Chain Processing Rules**:
  - **Power of Two Samples**: Enforce 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 sample limits
  - **Sample Length Normalization**: All samples in a chain must be equal length
  - **Padding Strategy**: Repeat last sample to fill unused slots
  - **Silence Padding**: Pad shorter samples with silence to match longest sample
- **File Size**: Handle files up to 1GB efficiently
- **Memory Usage**: Process files in chunks to minimize memory footprint

### Performance Targets
- **Processing Speed**: Process 1 minute of audio in under 10 seconds
- **Batch Efficiency**: Handle 100+ files in a single operation
- **Memory Efficiency**: Peak memory usage under 2GB for large files
- **CPU Utilization**: Utilize multiple cores when beneficial

### Output Quality
- **Audio Fidelity**: Maintain 95%+ quality compared to original
- **Sample Accuracy**: Precise timing within 1ms tolerance
- **Crossfade Quality**: Smooth transitions without artifacts
- **Metadata Accuracy**: Complete and accurate sample information

## Evenly Spaced Sample Chain Rules

### Core Concept
An "evenly spaced sample chain" is a single audio file containing multiple samples arranged sequentially, designed for slicing in samplers like the Digitakt 2. Each sample occupies a fixed time slot, allowing precise triggering and manipulation.

### Chain Structure Requirements

#### 1. Power of Two Sample Count
- **Mandatory**: All chains must contain exactly 2^n samples where n is an integer
- **Valid Counts**: 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
- **Current Limit**: Maximum 32 samples per chain (configurable)
- **Padding Strategy**: If a group has fewer than the next power of 2, repeat the last sample to fill remaining slots

#### 2. Sample Length Normalization
- **Equal Lengths**: All samples in a chain must be exactly the same length
- **Length Determination**: Use the longest sample in the group as the target length
- **Silence Padding**: Pad shorter samples with silence (zero amplitude) to match the longest sample
- **Timing Precision**: Maintain sample-accurate timing for consistent slicing

#### 3. Audio Format Standardization
- **Output Format**: 16-bit, 48kHz, Stereo (default)
- **Configurable Options**: 
  - Sample rate: 44.1kHz, 48kHz, 96kHz
  - Bit depth: 16-bit, 24-bit
  - Channels: Mono, Stereo
- **Quality Preservation**: Use high-quality resampling and dithering algorithms

### Example Chain Structure
```
Chain: drums-kick-1-3-32.wav
├── Sample 1:  Kick Aberlour 1.wav (padded to 2.5s)
├── Sample 2:  Kick Aberlour 2.wav (padded to 2.5s)
├── Sample 3:  Kick Aberlour 3.wav (padded to 2.5s)
├── Sample 4:  Kick Aberlour 3.wav (repeated)
├── Sample 5:  Kick Aberlour 3.wav (repeated)
...
├── Sample 32: Kick Aberlour 3.wav (repeated)
```

### Processing Workflow
1. **Group Analysis**: Identify samples that belong in the same chain
2. **Length Analysis**: Find the longest sample in the group
3. **Sample Normalization**: Pad all samples to match the longest length
4. **Power of Two Check**: Ensure the group size is a power of 2
5. **Padding**: Repeat the last sample to fill remaining slots
6. **Concatenation**: Combine all samples into a single audio file
7. **Format Conversion**: Convert to target format (16-bit, 48kHz, Stereo)
8. **Export**: Save with descriptive filename and metadata

## User Interface

### Command Line Interface
```bash
ni-sample-chainer [OPTIONS] INPUT_DIR OUTPUT_DIR

Options:
  --max-samples INT         Maximum samples per chain (must be power of 2, default: 32)
  --sample-rate INT         Output sample rate in Hz (default: 48000)
  --bit-depth INT           Output bit depth (16, 24, default: 16)
  --channels INT            Output channels (1=mono, 2=stereo, default: 2)
  --power-of-two           Enforce power of 2 sample count (default: true)
  --pad-strategy STRING     Padding strategy: repeat-last, silence, or none (default: repeat-last)
  --quality STRING          Quality preset (fast, standard, high)
  --parallel INT            Number of parallel processes
  --verbose                 Verbose output
  --dry-run                Show what would be processed without doing it
```

### Configuration File
- **YAML/JSON format** for persistent settings
- **Preset configurations** for common use cases
- **User-specific defaults** that can be overridden

## Project Structure

### Source Code Organization
```
src/
├── audio_processing/     # Core audio processing logic
│   ├── wav_handler.py    # WAV file input/output
│   ├── sample_generator.py # Sample chain generation
│   ├── quality_control.py # Audio quality management
│   └── metadata.py       # Metadata handling
├── digitakt_export/      # Digitakt 2 specific export
│   ├── formatter.py      # Format conversion
│   ├── naming.py         # Naming conventions
│   └── organizer.py      # File organization
├── utils/                # Utility functions
│   ├── file_utils.py     # File operations
│   ├── config.py         # Configuration management
│   └── logging.py        # Logging setup
└── main.py               # Main application entry point
```

### Testing Structure
```
tests/
├── unit/                 # Unit tests for individual functions
├── integration/          # Integration tests for complete workflows
├── audio_samples/        # Test audio files
└── fixtures/             # Test data and configurations
```

## Development Phases

### Phase 1: Core Audio Processing (Week 1-2)
- [ ] Basic WAV file handling
- [ ] Sample extraction with configurable duration
- [ ] Basic quality preservation
- [ ] Unit tests for core functions

### Phase 2: Sample Chain Generation (Week 3-4)
- [ ] Even spacing algorithm
- [ ] Overlap and crossfade implementation
- [ ] Metadata generation
- [ ] Integration tests

### Phase 3: Digitakt 2 Export (Week 5-6)
- [ ] Format compatibility
- [ ] Naming conventions
- [ ] File organization
- [ ] Export testing

### Phase 4: User Interface & Optimization (Week 7-8)
- [ ] Command line interface
- [ ] Configuration management
- [ ] Performance optimization
- [ ] User documentation

### Phase 5: Testing & Polish (Week 9-10)
- [ ] Comprehensive testing
- [ ] Performance benchmarking
- [ ] Bug fixes and refinements
- [ ] Final documentation

## Success Criteria

### Functional Requirements
- [ ] Successfully process WAV files of various sizes and qualities
- [ ] Generate evenly spaced samples with configurable parameters
- [ ] Export samples compatible with Digitakt 2
- [ ] Handle batch processing of multiple files
- [ ] Provide clear error messages and progress feedback

### Quality Requirements
- [ ] Maintain audio quality above 95% threshold
- [ ] Process audio at target speed (1 min in <10 seconds)
- [ ] Handle edge cases gracefully (corrupted files, unusual formats)
- [ ] Provide comprehensive logging and debugging information

### User Experience Requirements
- [ ] Simple, intuitive command line interface
- [ ] Clear progress indication during processing
- [ ] Helpful error messages with suggested solutions
- [ ] Comprehensive documentation and examples

## Risk Assessment

### Technical Risks
- **Audio Quality Loss**: Mitigation through extensive testing and quality metrics
- **Performance Issues**: Mitigation through profiling and optimization
- **Format Compatibility**: Mitigation through thorough testing with various WAV files

### Project Risks
- **Scope Creep**: Mitigation through clear phase definitions and success criteria
- **Testing Complexity**: Mitigation through automated testing and continuous integration
- **User Adoption**: Mitigation through clear documentation and examples

## Future Enhancements
- **Additional Audio Formats**: MP3, AIFF, FLAC support
- **Advanced Algorithms**: AI-powered sample selection
- **GUI Interface**: Graphical user interface for non-technical users
- **Cloud Integration**: Process files from cloud storage
- **Real-time Preview**: Listen to generated samples before export



