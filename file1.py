"""AI Image Classification using EfficientNet

This script classifies images using Google's EfficientNet-B0 model trained on ImageNet.
It can process local image files and predict the class of objects in the image.
"""
import torch
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification
from PIL import Image

# Load the pre-trained EfficientNet model and processor
preprocessor = EfficientNetImageProcessor.from_pretrained("google/efficientnet-b0")
model = EfficientNetForImageClassification.from_pretrained("google/efficientnet-b0")

# Load image from local file (ensure CATimg.png exists in the project directory)
image = Image.open("CATimg.png")
print(f"Processing image: CATimg.png")

# Preprocess the image for model input
inputs = preprocessor(image, return_tensors="pt")

# Run inference with no gradient computation for efficiency
with torch.no_grad():
    logits = model(**inputs).logits

# Get the predicted class (from 1000 ImageNet classes)
predicted_label = logits.argmax(-1).item()
predicted_class = model.config.id2label[predicted_label]

print(f"Predicted class: {predicted_class}")
