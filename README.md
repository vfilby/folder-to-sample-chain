# NI Sample Chainer

> ⚠️ **VIBE-CODED WARNING** ⚠️
> 
> This project was vibe-coded (though by someone who knows how to code) for a specific use case: creating sample chains for the Elektron Digitakt 2 from a particular audio library structure. While it's designed to be flexible, **results may vary** depending on your specific audio files, directory structure, and use case.
> 
> **Use at your own risk** and test thoroughly with your audio material before relying on it for production work.

---

A Python-based audio processing tool designed to create evenly spaced sample chains from local WAV files, specifically optimized for use with the Elektron Digitakt 2 sampler.

## 🎯 Project Overview

The NI Sample Chainer processes audio files to create consistent, evenly spaced samples that can be easily loaded into the Digitakt 2 for music production and performance. It's designed for musicians, producers, and sound designers who need to quickly convert long audio files into usable sample collections.

## ✨ Key Features

- **Batch Processing**: Process entire directories of WAV files at once
- **Even Spacing**: Generate samples at consistent temporal intervals
- **Quality Preservation**: Maintain audio fidelity throughout processing
- **Digitakt 2 Optimized**: Export in formats directly compatible with your device
- **Configurable Parameters**: Customize sample duration, overlap, crossfading, and more
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Audio processing libraries (will be specified in requirements.txt)

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

## 📁 Project Structure

```
ni-sample-chainer/
├── src/                    # Source code
│   ├── audio_processing/  # Core audio processing logic
│   ├── digitakt_export/   # Digitakt 2 specific export
│   ├── utils/             # Utility functions
│   └── main.py            # Main application entry point
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
├── output_samples/        # Generated sample output
├── AI_RULES.md            # AI development guidelines
├── PROJECT_SPEC.md        # Detailed project specification
└── README.md              # This file
```

## 🔧 Configuration

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

## 📊 Supported Audio Formats

### Input
- **Primary**: WAV (16-bit, 24-bit, 44.1kHz, 48kHz, 96kHz)
- **Future**: MP3, AIFF, FLAC

### Output
- **Format**: WAV (16-bit, 44.1kHz - Digitakt 2 standard)
- **Channels**: Mono and Stereo
- **Quality**: High-fidelity with configurable compression

## 🎵 Sample Chain Generation

The tool creates samples using an intelligent algorithm that:

1. **Analyzes** the input audio file for optimal sample points
2. **Generates** evenly spaced samples with configurable duration
3. **Applies** smooth crossfades between overlapping samples
4. **Exports** organized, named files ready for Digitakt 2

### Example Output Structure

```
output_samples/
├── original_song_001.wav
├── original_song_002.wav
├── original_song_003.wav
├── original_song_004.wav
└── metadata.json
```

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 📚 Documentation

- **[AI Rules](AI_RULES.md)**: Development guidelines and standards
- **[Project Specification](PROJECT_SPEC.md)**: Detailed technical requirements
- **[Examples](examples/)**: Usage examples and sample configurations

## 🤝 Contributing

We welcome contributions! Please read our development guidelines in `AI_RULES.md` and ensure all code follows the established standards.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes following the AI rules
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

[License information to be added]

## 🙏 Acknowledgments

- Built specifically for Elektron Digitakt 2 users
- Inspired by the need for efficient sample preparation workflows
- Built with modern Python audio processing libraries

## 📞 Support

For questions, issues, or feature requests:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the examples in the `examples/` folder

---

**Note**: This project is in active development. Features and APIs may change as we work toward the final release.



