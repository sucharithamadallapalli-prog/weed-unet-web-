# weed-unet-web
Flask app for U-Net weed segmentation.
1. `pip install -r requirements.txt`
2. The bundled model is at `models/smart_weed_unet.keras`. If replacing it, update `MODEL_PATH` in `config.py` (expected input: 256x256x3; output: 1-channel sigmoid; edit `IMG_SIZE` if different).
3. `python app.py` then open http://127.0.0.1:5000
