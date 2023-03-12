import os
from PIL import Image
from django.conf import settings

THUMBNAIL_SIZE = (200, 200)


def create_thumbnail(image, image_name):
    with Image.open(image) as im:
        im.thumbnail(THUMBNAIL_SIZE)
        im.save(os.path.join(settings.MEDIA_ROOT,
                f'thumbnails/{image_name}'))


def save_image_file(image, image_name):
    with Image.open(image) as im:
        im.save(os.path.join(settings.MEDIA_ROOT,
                f'profile_pictures/{image_name}'))
