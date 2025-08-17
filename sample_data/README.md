# Sample Data Directory

This directory is for testing the NI Sample Chainer with real audio files.

## Structure

```
sample_data/
├── input/          # Add your WAV files here for testing
├── output/         # Generated sample chains will be saved here
└── README.md       # This file
```

## How to Use

1. **Add your audio files** to the `input/` directory
   - Supported formats: WAV, AIFF, FLAC
   - Organize them in subdirectories if you want (e.g., `input/drums/kick/`, `input/drums/snare/`)
   - The system will analyze the directory structure and group files accordingly

2. **Run the processor** to generate sample chains
   - The system will automatically:
     - Convert all files to 16-bit, 48kHz, Stereo
     - Group files by directory structure
     - Create evenly spaced sample chains
     - Enforce power of 2 sample counts
     - Pad with repeated samples if needed

3. **Check the output** in the `output/` directory
   - Generated WAV files with descriptive names
   - JSON metadata files with chain information

## Example Directory Structure

```
input/
├── drums/
│   ├── kick/
│   │   ├── kick_1.wav
│   │   ├── kick_2.wav
│   │   └── kick_3.wav
│   ├── snare/
│   │   ├── snare_1.wav
│   │   └── snare_2.wav
│   └── hihat/
│       ├── closed_hh_1.wav
│       ├── closed_hh_2.wav
│       └── open_hh_1.wav
└── instruments/
    ├── bass/
    │   ├── bass_note_1.wav
    │   └── bass_note_2.wav
    └── lead/
        ├── lead_1.wav
        └── lead_2.wav
```

## Testing Commands

Once you've added your audio files, you can test with:

```bash
# Test the complete pipeline
python -m pytest tests/integration/test_audio_pipeline.py -v -s

# Run the demo with your files
python demo_audio_processing.py

# Or use the main application (when implemented)
python src/main.py sample_data/input sample_data/output
```

## Notes

- **CRITICAL SAFETY**: Source audio files are NEVER modified. All processing is done on copies in memory.
- Files will be automatically converted to the target format (16-bit, 48kHz, Stereo) (in memory only)
- Sample chains will be padded to power of 2 sample counts
- Hi-hat files will be interleaved if they share the same base name
- All other files will be grouped by directory structure
- Original files remain completely unchanged and safe
