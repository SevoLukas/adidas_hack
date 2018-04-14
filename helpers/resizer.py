import requests
from PIL import Image


def resize_and_upload(url, face_id, height, width, top, left):

    image = requests.get(url)
    unprocessed_image = Image.open(image)
    image_width, image_height = unprocessed_image.size

    width_px = image_width * width
    height_px = image_height * height
    left_px = image_width * left
    top_px = image_height * top

    crop = unprocessed_image.crop(left_px, top_px, width_px + left_px, top_px + height_px)

    # TODO: send crop file to S3, along with face_id
