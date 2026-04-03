"""Verify environment setup: FiftyOne, Twelve Labs API, and sample dataset."""

import os
from dotenv import load_dotenv

load_dotenv()

import fiftyone as fo
import fiftyone.zoo as foz
from twelvelabs import TwelveLabs

# Verify Twelve Labs API connection
api_key = os.environ["TWELVELABS_API_KEY"]
client = TwelveLabs(api_key=api_key)
indexes = client.indexes.list()
print(f"Twelve Labs connected. Indexes: {[idx.index_name for idx in indexes]}")

# Load sample video dataset
dataset = foz.load_zoo_dataset("quickstart-video", max_samples=3)
print(f"Dataset loaded: {dataset.name}, {len(dataset)} samples")

# Launch FiftyOne app
session = fo.launch_app(dataset)
print("FiftyOne app launched. Press Ctrl+C to exit.")
session.wait()
