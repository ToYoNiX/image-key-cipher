import numpy as np

def confuse_image(image, seed, reverse=False, perm=None):
    np.random.seed(seed)
    flat_image = image.reshape(-1, 3)

    if not reverse:
        perm = np.random.permutation(len(flat_image))
        confused_flat = flat_image[perm]
        confused_image = confused_flat.reshape(image.shape)
        return confused_image, perm  # Return permutation along with confused image
    else:
        if perm is None:
            raise ValueError("Permutation array is required for reversing confusion.")
        inverse_perm = np.argsort(perm)
        original_flat = flat_image[inverse_perm]
        original_image = original_flat.reshape(image.shape)
        return original_image

def lfsr(seed, taps, length):
    sr = seed
    xor = 0
    result = []

    for _ in range(length):
        xor = 0
        for t in taps:
            xor ^= (sr >> t) & 1
        sr = (sr << 1 | xor) & 0xFF  # keep 8-bit value
        result.append(sr)
    return result

def diffuse_image(image, seed, taps, reverse=False):
    flat_image = image.reshape(-1, 3)
    lfsr_stream = lfsr(seed, taps, len(flat_image) * 3)
    processed = []

    for i in range(len(flat_image)):
        r = flat_image[i][0] ^ lfsr_stream[i * 3]
        g = flat_image[i][1] ^ lfsr_stream[i * 3 + 1]
        b = flat_image[i][2] ^ lfsr_stream[i * 3 + 2]
        processed.append([r, g, b])

    processed_image = np.array(processed).reshape(image.shape)
    return processed_image
