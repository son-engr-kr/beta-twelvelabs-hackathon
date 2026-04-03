# Video Understanding Hackathon

FiftyOne plugin for video analysis powered by Twelve Labs API.

## Setup

### 1. Environment

```bash
# Create venv with Python 3.11.9
uv venv --python 3.11.9

# Activate
source .venv/Scripts/activate   # Windows (Git Bash)
source .venv/bin/activate       # macOS/Linux

# Install dependencies
uv pip install fiftyone twelvelabs huggingface_hub
```

### 2. API Key

```bash
export TWELVELABS_API_KEY="your-api-key-here"
```

Get your key at https://api.twelvelabs.io

### 3. Plugin Registration

Register the plugin so FiftyOne can discover it:

```bash
# Symlink plugin into FiftyOne's plugins directory
mkdir -p ~/fiftyone/__plugins__
ln -s "$(pwd)/plugin" ~/fiftyone/__plugins__/video-understanding-plugin
```

### 4. Verify Setup

```bash
python test_setup.py
```

This will:
- Connect to the Twelve Labs API
- Load a sample video dataset (3 clips from `quickstart-video`)
- Launch the FiftyOne app at `http://localhost:5151`

## Project Structure

```
├── plugin/
│   ├── fiftyone.yml    # Plugin metadata
│   ├── __init__.py     # VideoUnderstandingOperator
│   └── README.md       # Plugin docs
├── test_setup.py       # Setup verification script
└── README.md
```

## Usage

```bash
source .venv/Scripts/activate
export TWELVELABS_API_KEY="your-key"
python test_setup.py
```

Once the FiftyOne app is running, open the Operators panel and search for "Video Understanding" to use the plugin.
