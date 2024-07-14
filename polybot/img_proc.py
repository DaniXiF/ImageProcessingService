#pylint: disable=C0411,R0915,R1705,W1309
from pathlib import Path
from matplotlib.image import imread, imsave
import numpy as np


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        # TODO remove the `raise` below, and write your implementation
        self.data = np.rot90(self.data).tolist()


    def salt_n_pepper(self):
        height = len(self.data)
        width = len(self.data[0])
        for i in range(height):
            for j in range(width):
                if np.random.random() < 0.05:  # Randomly add salt and pepper noise to 5% of pixels
                    self.data[i][j] = 0  # Pepper
                elif np.random.random() < 0.05:
                    self.data[i][j] = 255  # Salt

    def concat(self, other_img, direction='horizontal'):
        if direction == 'horizontal':
            self.data = [row1 + row2 for row1, row2 in zip(self.data, other_img.data)]
        elif direction == 'vertical':
            self.data.extend(other_img.data)

    def segment(self):
        # TODO remove the `raise` below, and write your implementation
        raise NotImplementedError()
