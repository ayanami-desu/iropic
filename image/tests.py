from django.test import TestCase

# Create your tests here.

from .models import Images
import hashlib

def file_md5(web_file):
    data = web_file.open(mode='rb')
    return hashlib.md5(data).hexdigest()
all_image = Images.objects.all()
for image in all_image:
    image.md5 = file_md5(image.upload_file)
    image.save()
