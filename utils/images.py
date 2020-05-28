from PIL import Image
import os
import requests
from time import sleep
from .other import create_folder


class Worker:
    @staticmethod
    def square_cut(image, width, height, difference):
        return image.crop(((width - difference) // 2,
                           (height - difference) // 2,
                           (width + difference) // 2,
                           (height + difference) // 2))

    @staticmethod
    def horizontal_cut(image, width, height, difference):
        x1 = (width - difference) // 2
        y1 = 0
        x2 = (width + difference) // 2
        y2 = height
        return image.crop((x1, y1, x2, y2))

    @staticmethod
    def vertical_cut(image, width, height, difference):
        x1 = 0
        y1 = (height - difference) // 2
        x2 = width
        y2 = (height + difference) // 2
        return image.crop((x1, y1, x2, y2))

    @staticmethod
    def resizer(image, max_side, ratio):
        width, height = image.size
        if height > max_side \
                or width > max_side:
            if height >= width:
                height, width = max_side, int(max_side * ratio[0] / ratio[1])
            elif width > height:
                width, height = max_side, int(max_side * ratio[1] / ratio[0])
            return image.resize((width, height))
        return image


class Avatar:
    max_size = 512

    @staticmethod
    def adorable_avatar(abs_path, rel_path, email):
        response = requests.request('GET', rf'https://api.adorable.io/avatars/300/{email}')
        sleep(0.7)
        create_folder(abs_path)
        with open(os.path.join(abs_path, 'original.png'), 'wb') as original, \
                open(os.path.join(abs_path, 'cropped.png'), 'wb') as cropped:
            img_bytes = response.content
            original.write(img_bytes)
            cropped.write(img_bytes)
        return os.path.join(rel_path, 'cropped.png')

    def __init__(self, path):
        self.path = path

    def transform(self):
        images = list(os.walk(self.path))[0][2]
        name = None
        for image in images:
            if image.split('.')[0] != 'original':
                os.remove(os.path.join(self.path, image))
            else:
                name = image
        if name is not None:
            im = Image.open(os.path.join(self.path, name))
            im_w, im_h = im.size

            if im_w != im_h:
                im = Worker.square_cut(im, im_w, im_h, min(im.size))
            if any(side > self.max_size for side in im.size):
                im = Worker.resizer(im, self.max_size, (1, 1))
            extension = name.split('.')[-1]
            destination = os.path.join(self.path, f'cropped.{extension}')
            im.save(destination, quality=100)
            return f'cropped.{extension}'
        return


class Plates:
    ratio = {
        1: ((1, 1), (1, 1), (1, 1), (1, 1)),
        2: ((2, 3), (4, 3), (4, 3), (2, 3)),
        3: ((4, 1), (4, 1), (4, 1), (4, 1)),
        4: ((2, 1), (2, 3), (2, 3), (2, 3)),
    }
    max_size = 1000

    def __init__(self, user_template: int, directory: str):
        self.template = user_template
        self.path = directory

    def transform(self):
        images = list(os.walk(self.path))[0][2]
        for image in images:
            if image.split('_')[0] != 'original':
                os.remove(os.path.join(self.path, image))
        images = sorted(list(image for image in images if image.split('_')[0] == 'original'))
        for ratio, image in zip(self.ratio[self.template], images):
            im = Image.open(os.path.join(self.path, image))

            im_w, im_h = im.size
            if im_w/im_h > ratio[0]/ratio[1]:
                new_w = int(ratio[0]*im_h/ratio[1])
                im = Worker.horizontal_cut(im, im_w, im_h, new_w)
            elif im_w/im_h < ratio[0]/ratio[1]:
                new_h = int(ratio[1]*im_w/ratio[0])
                im = Worker.vertical_cut(im, im_w, im_h, new_h)
            if any(side > self.max_size for side in im.size):
                im = Worker.resizer(im, self.max_size, ratio)

            destination = os.path.join(self.path, image.split('_')[1])
            im.save(destination, quality=100)
            yield image.split('_')[1]


if __name__ == '__main__':
    p = Plates('gogi@gogi.gogi', 1)
    p.transform()
