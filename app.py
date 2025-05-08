from flask import Flask, render_template, request
from io import BytesIO
import base64
from datetime import datetime
import hashlib

import numpy as np
from PIL import Image, PngImagePlugin

from helpers import confuse_image, diffuse_image

app = Flask(__name__)

def generate_seed(timestamp: str, salt: str) -> int:
    """Generate a reproducible seed from timestamp and salt"""
    hash_val = hashlib.sha256((timestamp + salt).encode()).hexdigest()
    return int(hash_val, 16) % (2**32)

@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    file = request.files["image"]
    image = Image.open(file.stream).convert("RGB")
    image_np = np.array(image)

    # Generate a timestamp and seed
    timestamp = datetime.utcnow().isoformat()
    seed = generate_seed(timestamp, salt="my_secret_salt")

    # Encrypt image
    confused_image, confusion_perm = confuse_image(image_np, seed=seed)
    encrypted_image = diffuse_image(confused_image, seed=seed, taps=[7, 5, 4, 3])

    # Save encrypted image with timestamp metadata
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("timestamp", timestamp)
    metadata.add_text("confusion_perm", str(confusion_perm.tolist()))  # Store permutation as string

    output_buffer = BytesIO()
    Image.fromarray(encrypted_image.astype(np.uint8)).save(output_buffer, format="PNG", pnginfo=metadata)
    base64_img = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

    return render_template("home.html", image_data=base64_img, action="Encrypted")

@app.route("/decrypt", methods=["POST"])
def decrypt():
    file = request.files.get("image")
    if not file:
        return "No image uploaded for decryption."

    # Read encrypted image
    img = Image.open(file.stream).convert("RGB")

    # Try to extract timestamp and permutation from image metadata
    timestamp = None
    confusion_perm = None

    if hasattr(img, "info") and "timestamp" in img.info:
        timestamp = img.info["timestamp"]
    if hasattr(img, "info") and "confusion_perm" in img.info:
        confusion_perm = np.array(eval(img.info["confusion_perm"]))  # Convert string back to list/array

    # Check if timestamp exists
    if not timestamp or confusion_perm is None:
        return "Missing encryption metadata."

    # Generate seed based on timestamp
    seed = generate_seed(timestamp, salt="my_secret_salt")
    image_np = np.array(img)

    # Decrypt image using the generated seed
    recovered_diffused = diffuse_image(image_np, seed=seed, taps=[7, 5, 4, 3], reverse=True)
    recovered_image = confuse_image(recovered_diffused, seed=seed, reverse=True, perm=confusion_perm)

    # Convert decrypted image to base64 for rendering in the template
    output_buffer = BytesIO()
    Image.fromarray(recovered_image.astype(np.uint8)).save(output_buffer, format="PNG")
    base64_img = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

    return render_template("home.html", image_data=base64_img, action="Decrypted")

if __name__ == "__main__":
    app.run(debug=True)
