import cv2
import numpy as np
from nnconfig import *

"""
images2array　
    与えられたパスの画像をnp.arrayへ変換し結合して1次元にしたものを返す(画像はグレースケールへ変換される)

Inputs
----------
image_paths : list string [フレーム数]
    各画像のpathが格納されている

Outputs
----------
images_flatten : np.array np.float32 [IMAGE_SIZE * IMAGE_SIZE * フレーム数]
    各画像をグレースケールにしてさらに1次元に変換し, 結合させたもの
"""
def images2array(image_paths):
    images = []
    for image_path in image_paths:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print('not image:', image_path)
            return None

        # リサイズ&正規化
        image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
        image = image.flatten().astype(np.float32) / 255.0
        images.append(image)

    images_flatten = np.array(images).flatten()
    return images_flatten