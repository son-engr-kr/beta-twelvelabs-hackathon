# Video Understanding Plugin

FiftyOne plugin for video analysis powered by Twelve Labs API.

## Description

Integrates Twelve Labs video understanding capabilities into the FiftyOne app, enabling natural language video analysis directly from the dataset browser.

## Installation

```bash
# Register the plugin with FiftyOne
fiftyone plugins create plugin/

# Or symlink to FiftyOne plugins directory
ln -s $(pwd)/plugin ~/.fiftyone/plugins/video-understanding-plugin
```

## Usage

1. Launch FiftyOne App
2. Open the Operators panel
3. Search for "Video Understanding"
4. Enter a prompt and run

## Requirements

- `fiftyone`
- `twelvelabs`
- `TWELVELABS_API_KEY` environment variable set
