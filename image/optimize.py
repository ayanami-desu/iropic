from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

def pic_optimize(pic, aim_type):
# pic是 <class 'django.core.files.uploadedfile.InMemoryUploadedFile'> 类型的数据
# 而pillow的Image.open("./xxx.jpg") 则是：<class 'PIL.JpegImagePlugin.JpegImageFile'> 类型的数据
# 问题是如何把InMemoryUploadedFile转化为PIL类型，并且处理之后再转回InMemoryUploadedFile，并save
    im_pic = Image.open(pic).convert('RGB')
#先保存到磁盘io
    pic_io = BytesIO()
    im_pic.save(pic_io, aim_type)
#再转化为InMemoryUploadedFile数据 
    pic_file = InMemoryUploadedFile(
    file=pic_io,
    field_name=None,
    name=pic.name,
    content_type=aim_type,
    size=pic.size,
    charset=None
    )
    return pic_file