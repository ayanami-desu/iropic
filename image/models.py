from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from datetime import datetime

class Labels(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

class Albums(models.Model):
    name = models.CharField(max_length=20, unique=True)
    cover = models.FileField(max_length=200, blank=True, null=True)
    created_time = models.DateTimeField(auto_now=True)
    desc = models.CharField(max_length=200, blank=True, null=True)
    isR18 = models.BooleanField(null=True, blank=True, default=False)

def return_dir(instance, filename):
    n = filename[::-1].index('.') 
    only_filename = filename[:-n-1]# 文件名
    m = instance.file_type.index('/')#文件格式
    file_type = instance.file_type[m+1:]
    last_modified = datetime.fromtimestamp(float(instance.edit_time)/1000).strftime(r'%Y-%m-%d')
    return 'gallary/{}/{}.{}'.format(last_modified, only_filename, file_type)

def return_webp_dir(instance,filename):
    last_modified = datetime.fromtimestamp(float(instance.edit_time)/1000).strftime(r'%Y-%m-%d')
    n = filename[::-1].index('.') #获取文件全名中点的位置
    only_filename = filename[:-n-1]# 文件名
    return 'optimized/{}/{}.webp'.format(last_modified, only_filename)


class Images(models.Model):
    belong_to_album = models.ForeignKey(Albums, on_delete=models.SET_NULL, null=True, blank=True)
    upload_file = models.FileField(upload_to=return_dir, max_length=200, blank=True, null=True)
    thumbnail_file = models.FileField(upload_to=return_webp_dir, max_length=200, blank=True, null=True)
    edit_time = models.CharField(max_length=30, blank=True, null=True)# 原始修改时间
    labels = models.ManyToManyField(Labels, blank=True)# 图片标签
    origin_filename = models.CharField(max_length=200, blank=True, null=True)#文件原始名称
    file_type = models.CharField(max_length=10, blank=True, null=True)# 文件原始类型
    isR18 = models.BooleanField(null=True, blank=True,default=False)
    author = models.CharField(max_length=30, blank=True, null=True, default='未知')
    md5 = models.CharField(max_length=50, unique=True, blank=True, null=True)

@receiver(pre_delete, sender=Images)
def upload_file_deleted(instance, *args, **kwargs):
    print('准备删除文件')
    instance.upload_file.delete(save=False)
    instance.thumbnail_file.delete(save=False)
