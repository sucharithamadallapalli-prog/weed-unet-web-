
import numpy as np
from PIL import Image
from flask import current_app

from app.services.unet_service import get_model


def predict_image(image_path, mask_path, result_path):

    # Image size from configuration
    size = current_app.config.get("IMG_SIZE", 256)

    # Load original image
    original = Image.open(image_path).convert("RGB")
    resized = original.resize((size, size))

    # Prepare image for U-Net
    image_array = np.asarray(resized, dtype=np.float32) / 255.0
    batch = np.expand_dims(image_array, axis=0)

    # Get model prediction (memory optimization)
    prediction = get_model()(batch, training=False).numpy()

    # Check model output
    if prediction.ndim != 4 or prediction.shape[-1] != 3:
        raise ValueError(
            f"Unexpected model output: {prediction.shape}"
        )

    # Predicted class for each pixel
    mask = np.argmax(prediction[0], axis=-1).astype(np.uint8)

    # Class 1 is assumed to represent weeds
    weed_pixels = (mask == 1)

    # Calculate weed coverage
    coverage = float(np.mean(weed_pixels) * 100)

    # Calculate average confidence for predicted weed pixels
    if np.any(weed_pixels):
        confidence = float(
            np.mean(prediction[0, :, :, 1][weed_pixels]) * 100
        )
    else:
        confidence = 0.0

    # Create visible binary mask
    # White = detected weeds
    # Black = other classes
    binary_mask = np.where(
        weed_pixels, 255, 0
    ).astype(np.uint8)

    Image.fromarray(binary_mask, mode="L").save(mask_path)

    # Color map:
    # Class 0 = Background (black)
    # Class 1 = Weed (green)
    # Class 2 = Crop (red)
    colors = np.array([
        [0, 0, 0],
        [0, 255, 0],
        [255, 0, 0]
    ], dtype=np.uint8)

    colored_mask = colors[mask]

    # Create segmentation overlay
    overlay = (
        0.6 * np.asarray(resized, dtype=np.float32)
        + 0.4 * colored_mask.astype(np.float32)
    ).clip(0, 255).astype(np.uint8)

    Image.fromarray(overlay).save(result_path)

    # Return analysis results
    return {
        "weed_coverage": round(coverage, 2),
        "weed_confidence": round(confidence, 2)
    }
