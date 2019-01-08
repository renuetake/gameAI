import cv2
import numpy as np
from nnconfig import *

def resize_images(image_arrays):
    """
    images2array　
        与えられたパスの画像をnp.arrayへ変換し結合して1次元にしたものを返す(画像はグレースケールへ変換される)

    Inputs
    ----------
    image_paths : np.array float [フレーム数, width, height]
        各画像がnp.arrayで格納されている

    Outputs
    ----------
    images_flatten : np.array np.float32 [IMAGE_SIZE * IMAGE_SIZE * フレーム数]
        各画像をグレースケールにしてさらに1次元に変換し, 結合させたもの
    """
    images = []
    for image_array in image_arrays:
        # リサイズ&正規化
        resized_image = cv2.resize(image_array, (IMAGE_SIZE, IMAGE_SIZE))
        flatten_image = resized_image.flatten().astype(np.float32) / 255.0
        images.append(flatten_image)

    images_flatten = np.array(images).flatten()
    return images_flatten