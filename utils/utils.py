from PIL import Image
import base64
import urllib
import io
def byteify(input, encoding='utf-8'):
    """
    Encode all the values in the input data
    :param input: input data, can be nested dict and list data structure
    :param encoding: encoding format
    :return: encoded data
    """
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encoding)
    else:
        return input

def get_image_uri(image_bytes):
    image_base64 = base64.b64encode(image_bytes)
    image_type = Image.open(io.BytesIO(image_bytes)).format
    url = "data:image/" + image_type + ";base64," + image_base64
    return url

def get_image_thumbnail(image_bytes, size = (224,224)):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image.thumbnail(size, Image.ANTIALIAS)
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='jpeg')
    return imgByteArr.getvalue()

import oss2
oss2.Bucket().put_object_with_url_from_file()
