from flask import Flask, render_template, request, send_file
import numpy as np
import cv2
import os
from helpers import confuse_image, diffuse_image

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

confusion_perm = None  # To store the permutation for decryption

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("home.html")


@app.route("/encrypt", methods=['POST'])
def encrypt():
    global confusion_perm

    # Upload and read image
    file = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted.png')
    file.save(path)

    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Confusion + Diffusion
    confused_image, confusion_perm = confuse_image(image, seed=42)
    encrypted_image = diffuse_image(confused_image, seed=123, taps=[7, 5, 4, 3])

    # Save encrypted image
    encrypted_bgr = cv2.cvtColor(encrypted_image.astype(np.uint8), cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, encrypted_bgr)

    return send_file(path, mimetype='image/png')


@app.route("/decrypt", methods=['POST'])
def decrypt():
    global confusion_perm

    # Load the encrypted image
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted.png')
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Reverse diffusion and confusion
    recovered_diffused = diffuse_image(image, seed=123, taps=[7, 5, 4, 3], reverse=True)
    if confusion_perm is None:
        return "Confusion permutation not found. Please encrypt an image first."

    recovered_image = confuse_image(recovered_diffused, seed=42, reverse=True, perm=confusion_perm)

    # Save and return
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted.png')
    recovered_bgr = cv2.cvtColor(recovered_image.astype(np.uint8), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, recovered_bgr)

    return send_file(output_path, mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True)
