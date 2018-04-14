import requests
import boto3
import os
import logging
from PIL import Image
from io import BytesIO, StringIO


s3 = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY', ),
                          aws_secret_access_key=os.getenv('AWS_SECRET'),
                          region_name='eu-west-1')
BUCKET = 'rekognition-adihack'


async def resize_and_upload(url, face_id, height, width, top, left):
    try:
        response = requests.get(url)
        unprocessed_image = Image.open(BytesIO(response.content))
        image_width, image_height = unprocessed_image.size
        width = round(image_width * float(width))
        height = round(image_height * float(height))
        left = round(image_width * float(left))
        top = round(image_height * float(top))
        crop = unprocessed_image.crop((left,
                                       top,
                                       width + left,
                                       top + height))
        file_name = '{}.jpg'.format(face_id)
        crop.save(file_name, 'JPEG')
        with open(file_name, 'rb') as f:
            s3.Bucket(BUCKET).put_object(Body=f, Key='faces/{}.jpg'.format(face_id))
        os.remove(file_name)
    except Exception as e:
        logging.error(e)
    return 'ok'
