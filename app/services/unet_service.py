
import json
import os
import numpy as np
from flask import current_app

_model = None


def get_model():
    """Load the U-Net model once per process."""
    global _model

    if _model is None:
        import tensorflow as tf

        model_path = current_app.config["MODEL_PATH"]
        config_path = os.path.join(model_path, "config.json")
        weights_path = os.path.join(model_path, "model.weights.h5")

        if not os.path.isfile(config_path):
            raise FileNotFoundError(
                f"Model configuration not found: {config_path}"
            )

        if not os.path.isfile(weights_path):
            raise FileNotFoundError(
                f"Model weights not found: {weights_path}"
            )

        # Read the saved model architecture
        with open(config_path, "r", encoding="utf-8") as file:
            model_config = json.load(file)

        # Remove training configuration if present
        model_config.pop("compile_config", None)

        # Rebuild the model architecture
        _model = tf.keras.models.model_from_json(
            json.dumps(model_config)
        )

        # Load the trained model weights
        _model.load_weights(weights_path)

        print("U-Net model loaded successfully!")
        print("Input shape:", _model.input_shape)
        print("Output shape:", _model.output_shape)

    return _model


def predict_mask(batch):
    """
    Predict segmentation probabilities.

    Input shape: (N, 256, 256, 3)
    Output shape: (N, 256, 256, 3)
    """
    batch = np.asarray(batch, dtype=np.float32)

    predictions = get_model().predict(batch, verbose=0)

    if predictions.ndim != 4 or predictions.shape[-1] != 3:
        raise ValueError(
            f"Unexpected model output shape: {predictions.shape}"
        )

    return predictions
