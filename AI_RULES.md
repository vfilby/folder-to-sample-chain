# AI Development Rules for NI Sample Chainer

## Project Overview
This project processes local audio WAV files to create evenly spaced sample chains for the Elektron Digitakt 2 sampler.

## Core Development Principles

### 1. Audio Processing Standards
- **Format Support**: Primary focus on WAV files (16-bit, 44.1kHz recommended)
- **Quality Preservation**: Maintain audio quality throughout processing chain
- **Memory Efficiency**: Process files in chunks when dealing with large audio files
- **Error Handling**: Graceful handling of corrupted or unsupported audio files

### 2. Digitakt 2 Compatibility
- **Sample Rate**: Ensure output samples are compatible with Digitakt 2 specifications
- **File Format**: Export in formats directly usable by the Digitakt 2
- **Naming Convention**: Use clear, descriptive names that work with Digitakt 2 file system
- **Size Limits**: Respect any file size or duration limitations of the target device

### 3. Sample Chain Generation
- **Even Spacing**: Create samples with consistent temporal intervals
- **Crossfading**: Implement smooth transitions between samples when appropriate
- **Metadata**: Preserve and generate relevant sample information
- **Batch Processing**: Efficiently handle multiple input files

### 4. Code Quality Standards
- **Python Best Practices**: Follow PEP 8, type hints, docstrings
- **Modular Design**: Separate concerns into logical modules
- **Testing**: Comprehensive test coverage for audio processing functions
- **Documentation**: Clear API documentation and usage examples

### 5. User Experience
- **Command Line Interface**: Simple, intuitive CLI for batch processing
- **Progress Feedback**: Clear indication of processing status
- **Error Messages**: Helpful error messages with suggested solutions
- **Configuration**: Flexible configuration options for different use cases

### 6. Performance Considerations
- **Multiprocessing**: Utilize multiple cores for batch processing when beneficial
- **Memory Management**: Efficient memory usage for large audio files
- **Caching**: Implement caching for repeated operations
- **Profiling**: Monitor performance bottlenecks and optimize accordingly

### 7. File Management
- **Input Validation**: Verify input files before processing
- **Output Organization**: Clear structure for generated sample chains
- **Backup Strategy**: Preserve original files, never modify in place
- **Logging**: Comprehensive logging for debugging and audit trails

### 8. AI Development Rules
- **No One-Off Scripts**: Always use main application code and existing test framework
- **Short Summaries**: Keep explanations and summaries concise and focused
- **Test Integration**: Use existing pytest infrastructure for all testing
- **Code Reuse**: Leverage existing classes and methods instead of creating new ones
- **Documentation**: Update existing docs rather than creating separate explanations

## Development Workflow
1. **Plan**: Define requirements and design before implementation
2. **Implement**: Follow established patterns and standards
3. **Test**: Verify functionality with various audio file types
4. **Document**: Update documentation for any new features
5. **Review**: Code review focusing on audio quality and performance

## Audio-Specific Considerations
- **Sample Rate Conversion**: Handle different input sample rates appropriately
- **Bit Depth**: Maintain or convert bit depth as needed
- **Channels**: Support mono and stereo files
- **Duration**: Handle files of varying lengths gracefully
- **Format Validation**: Verify WAV file integrity before processing

## Testing Strategy
- **Unit Tests**: Test individual audio processing functions
- **Integration Tests**: Test complete sample chain generation
- **Audio Quality Tests**: Verify output quality meets standards
- **Performance Tests**: Ensure processing speed meets requirements
- **Edge Case Tests**: Handle unusual audio files and error conditions



