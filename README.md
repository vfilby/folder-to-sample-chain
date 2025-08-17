# NI Sample Chainer

> ⚠️ **VIBE-CODED WARNING** ⚠️
> 
> This project was vibe-coded (though by someone who knows how to code) for a specific use case: creating sample chains for the Elektron Digitakt 2 from a particular audio library structure. While it's designed to be flexible, **results may vary** depending on your specific audio files, directory structure, and use case.
> 
> **Use at your own risk** and test thoroughly with your audio material before relying on it for production work.

---

A Python-based audio processing tool designed to create evenly spaced sample chains from local WAV files, specifically optimized for use with the Elektron Digitakt 2 sampler.

## Project Overview

The NI Sample Chainer processes audio files to create consistent, evenly spaced samples that can be easily loaded into the Digitakt 2 for music production and performance. It's designed for musicians, producers, and sound designers who need to quickly convert long audio files into usable sample collections.

## Key Features

- **Batch Processing**: Process entire directories of WAV files at once
- **Even Spacing**: Generate samples at consistent temporal intervals
- **Quality Preservation**: Maintain audio fidelity throughout processing
- **Digitakt 2 Optimized**: Export in formats directly compatible with your device
- **Configurable Parameters**: Customize sample duration, overlap, crossfading, and more
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Audio processing libraries (specified in requirements.txt)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ni-sample-chainer

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Process a directory of WAV files
python src/main.py input_audio_directory output_samples

# With custom parameters
python src/main.py input_dir output_dir \
  --sample-duration 2.0 \
  --overlap 25 \
  --crossfade 100 \
  --quality high
```

## Project Structure

```
ni-sample-chainer/
├── src/                    # Source code
│   ├── audio_processing/  # Core audio processing logic
│   ├── digitakt_export/   # Digitakt 2 specific export
│   ├── utils/             # Utility functions
│   └── main.py            # Main application entry point
├── tests/                 # Test suite
├── sample_data/           # Test audio samples
├── config.yaml            # Configuration file
├── requirements.txt        # Python dependencies
├── AI_RULES.md            # AI development guidelines
├── PROJECT_SPEC.md        # Detailed project specification
└── README.md              # This file
```

## Configuration

The tool supports both command-line options and configuration files. Create a `config.yaml` file in your project directory:

```yaml
# Default processing settings
defaults:
  sample_duration: 1.0      # seconds
  overlap: 0                # percentage
  crossfade: 50            # milliseconds
  quality: standard         # fast, standard, high
  parallel_processes: 4

# Digitakt 2 specific settings
digitakt:
  output_format: wav
  sample_rate: 44100
  bit_depth: 16
  naming_convention: "{original_name}_{sample_number:03d}"
```

## Supported Audio Formats

### Input
- **Primary**: WAV (16-bit, 24-bit, 44.1kHz, 48kHz, 96kHz)
- **Secondary**: MP3, AIFF, FLAC

### Output
- **Format**: WAV (16-bit, 48kHz - Digitakt 2 standard)
- **Channels**: Stereo (configurable to mono)
- **Quality**: High-fidelity with configurable compression

## Sample Chain Generation

The tool intelligently groups audio files and creates sample chains based on:

1. **Hi-hat Detection**: Automatically identifies closed and open hi-hat samples
2. **Directory Structure**: Groups samples by their folder organization
3. **Smart Interleaving**: Combines related samples into logical chains
4. **Power-of-Two Optimization**: Ensures chains have optimal sample counts for samplers

## Directory Structure Examples

### Input Structure
```
sample_data/
├── input/
│   ├── samples 2/
│   │   ├── closedhh/
│   │   │   ├── sample hat1.wav
│   │   │   ├── sample hat2.wav
│   │   │   └── sample hat3.wav
│   │   ├── openhh/
│   │   │   ├── sample hat1 1.wav
│   │   │   ├── sample hat1 2.wav
│   │   │   ├── sample hat2.wav
│   │   │   └── sample hat3.wav
│   │   ├── kick/
│   │   │   ├── sample hollow.wav
│   │   │   └── sample sharp.wav
│   │   ├── clap/
│   │   │   ├── sample double.wav
│   │   │   └── sample tank.wav
│   │   ├── perc/
│   │   │   ├── A06.wav
│   │   │   ├── A07.wav
│   │   │   └── A08.wav
│   │   └── sfx/
│   │       └── 495310__boryslaw_kozielski__test-stereo.mp3
│   └── Loops/              # Excluded from processing
│       └── loop_samples.wav
```

### Output Structure
```
output_directory/
├── CHAIN_SUMMARY.md        # Chain summary (in root)
├── chains/                 # Sample chain WAV files ONLY
│   ├── hats_1-8-0.882s.wav
│   ├── samples 2-kick-2-0.462s.wav
│   ├── samples 2-perc-4-0.404s.wav
│   ├── samples 2-clap-2-0.520s.wav
│   └── samples 2-sfx-1-30.338s.wav
└── metadata/               # Configuration + Individual JSON metadata files
    ├── chain_config.yaml
    ├── hats_1-8-0.882s.json
    ├── samples 2-kick-2-0.462s.json
    ├── samples 2-perc-4-0.404s.json
    ├── samples 2-clap-2-0.520s.json
    └── samples 2-sfx-1-30.338s.json
```

## Hi-hat Chain Generation

The tool creates intelligent hi-hat chains by:

1. **Detecting hi-hat types**: Identifies closed and open hi-hat samples
2. **Grouping by base name**: Groups samples with the same underlying sound
3. **Interleaving pattern**: Places closed samples first, then open samples
4. **Maintaining integrity**: Keeps all samples of the same hi-hat name together

Example hi-hat chain structure:
```
hats_1: 8 samples
├── closedhh/sample hat1.wav      # Closed hi-hat
├── openhh/sample hat1 1.wav      # Open hi-hat variant 1
├── openhh/sample hat1 2.wav      # Open hi-hat variant 2
├── closedhh/sample hat2.wav      # Closed hi-hat
├── openhh/sample hat2.wav        # Open hi-hat
├── closedhh/sample hat3.wav      # Closed hi-hat
├── openhh/sample hat3.wav        # Open hi-hat
└── [padded to power of 2]
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python run_tests.py

# Run with pytest directly
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
python setup_dev.py

# Run linting and formatting
python -m black src/
python -m flake8 src/
```

### Project Architecture

- **Modular Design**: Separated concerns for audio processing, chain planning, and export
- **Configuration Driven**: YAML-based configuration for easy customization
- **Test Coverage**: Comprehensive testing with real audio samples
- **Error Handling**: Robust error handling and user feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is provided as-is for educational and personal use. See the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the PROJECT_SPEC.md for technical details
- Check the TESTING_GUIDE.md for troubleshooting

---

*Generated by NI Sample Chainer*



