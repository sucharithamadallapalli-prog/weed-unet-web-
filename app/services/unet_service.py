import json
import os
import numpy as np
from flask import current_app

# Limit CPU/thread memory overhead before TensorFlow loads
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"

_model = None


def get_model():
    """Load the U-Net model once and reuse it."""
    global _model

    if _model is None:
        import tensorflow as tf

        # Limit TensorFlow threading
        try:
            tf.config.threading.set_intra_op_parallelism_threads(1)
            tf.config.threading.set_inter_op_parallelism_threads(1)
        except RuntimeError:
            pass

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

        # Read architecture
        with open(config_path, "r", encoding="utf-8") as file:
            model_config = json.load(file)

        model_config.pop("compile_config", None)

        # Build model
        _model = tf.keras.models.model_from_json(
            json.dumps(model_config)
        )

        # Load trained weights
        _model.load_weights(weights_path)

        print("U-Net model loaded successfully!")
        print("Input shape:", _model.input_shape)
        print("Output shape:", _model.output_shape)

    return _model


def predict_mask(batch):
    """Run segmentation inference with minimal extra overhead."""

    import tensorflow as tf

    batch = np.asarray(batch, dtype=np.float32)

    # Direct inference instead of model.predict()
    output = get_model()(batch, training=False)

    predictions = output.numpy()

    if predictions.ndim != 4 or predictions.shape[-1] != 3:
        raise ValueError(
            f"Unexpected model output shape: {predictions.shape}"
        )

    return predictions