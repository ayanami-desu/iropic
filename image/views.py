from django.http import JsonResponse, FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .serializers import *
from .models import Images, Labels, Albums, upload_file_deleted
from .optimize import pic_optimize
import hashlib

def file_md5(web_file):
    data = web_file.open(mode='rb').read()
    return hashlib.md5(data).hexdigest()



def tool(request):
    all_image = Images.objects.all()
    for image in all_image:
        image.md5 = file_md5(image.upload_file)
        image.save()
    return JsonResponse({'msg':'完成'})

class ImageApi(APIView):
    def get(slef, request):
        #根据图片id返回图片
        file_type = request.GET.get('fileType', 'webp')
        #支持的文件格式，jpeg,webp,origin
        try:
            pid = request.GET['pid']
            image = Images.objects.get(id=pid)
            if file_type == 'webp':
                #不带参数，或参数为webp均返回webp缩略图
                return FileResponse(image.thumbnail_file)
            elif file_type == 'origin':
                #返回原图
                return FileResponse(image.upload_file)
            else:
                return Response({'msg':'不支持的文件类型'}, status=400)
        except Exception as e:
            print(e)
            return Response({'err':str(e)}, status=404)
    def post(self, request):
        #获取图片对象，以列表形式返回
        try:
            page = int(request.data.get('page', -1))
            num = int(request.data.get('num', -1))
            sort_by = request.data.get('sortBy', 'down')
            if num>16:
                return Response({'msg':'超过一次请求限制最大数量'}, status=400)
            if page<0 or num<0:
                return Response({'msg': '无效参数'}, status=400)
            album_id = request.data.get('albumId', None)
            tags = request.data.get('tags', None)
            mode = request.data.get('mode', 'or')
            if not request.auth:
                images = Images.objects.all().exclude(isR18=True)
            else:
                images = Images.objects.all()
            if album_id:
                images = images.filter(belong_to_album=album_id)
            if tags:
                tag_list = tags.split(',')
                if mode == 'or':
                    images = images.filter(labels__name__in = tag_list).distinct()
                elif mode == 'and':
                    for i in range(len(tag_list)):
                        images = images.filter(labels__name=tag_list[i])
            images_num = images.count()
            if sort_by == 'up':
                images = images.order_by('edit_time')[(page-1)*num : page*num]
            elif sort_by == 'down':
                images = images.order_by('-edit_time')[(page-1)*num : page*num]
            data = ImageListSerializer(images, many=True).data
            return Response({'data':data, 'imageNum':images_num})
        except Exception as e:
            print(e)
            return Response({'err':str(e)}, status=400)
    def delete(self, request):
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid_list = request.data.get('pidList', None)
        if pid_list:
            try:
                for pid in pid_list:
                    image = Images.objects.get(id=pid)
                    upload_file_deleted(image)
                    image.delete()
                return Response({'msg':'删除完成'})
            except Exception as e:
                print(e)
                return Response({'err':str(e)}, status=400)
        else:
            return Response({'msg': '无效参数'}, status=400)

class ImageData(APIView):
    def get(self, request):
        #获取图片的全部信息
        pid = request.GET['pid']
        try:
            image = Images.objects.get(id=pid)
            image_data = ImageSerializer(image).data
            return Response({'data':image_data, 'size': image.upload_file.size})
        except Exception as e:
            print(e)
            return Response({'msg':'获取图片信息失败','err':str(e)}, status=400)    
    def put(self, request):
        #为图片增加标签，支持增加多个
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid = request.data['pid']
        labels = request.data['labels']
        try:
            image = Images.objects.get(id=pid)
            label_list = labels.split(',')
            for label in label_list:
                the_label = Labels.objects.get(name=label)
                image.labels.add(the_label)
            return Response({'msg':'添加成功'})
        except Exception as e:
            print(e)
            return Response({'msg':'添加失败','err':str(e)}, status=400)
    def delete(self, request):
        #为图片删除标签
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid = request.data.get('pid', None)
        label = request.data.get('label', None)
        if pid and label:
            try:
                image = Images.objects.get(id=pid)
                the_label = Labels.objects.get(name=label)
                image.labels.remove(the_label)
                return Response({'msg':'删除成功'})
            except Exception as e:
                print(e)
                return Response({'msg':'删除失败','err':str(e)}, status=400)
        else:
            return Response({'err': '参数无效'}, status=400)
class ImageR18(APIView):
    def post(self, request):
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid_list = request.data.get('pidList', None)
        if not pid_list:
            return Response({'msg': '无效参数'}, status=400)
        for pid in pid_list:
            img = Images.objects.get(id=int(pid))
            img.isR18 = True
            img.save(update_fields=['isR18'])
        return Response({'msg':'成功'})
    def put(self,request):
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid_list = request.data.get('pidList', None)
        if not pid_list:
            return Response({'msg': '无效参数'}, status=400)
        for pid in pid_list:
            img = Images.objects.get(id=int(pid))
            img.isR18 = False
            img.save(update_fields=['isR18'])
        return Response({'msg':'成功'})

@api_view(['POST'])
def image_handle(request):
    #文件上传
    if not request.auth:
        return Response({'msg':'permission denied'}, status=401)
    the_file = request.FILES.get('file',None)
    data = request.data
    if the_file:
        db_data = {
            'upload_file': the_file,
            'edit_time': data['lastModified'],
            'origin_filename': data['name'],
            'file_type': data['fileType'],
            'thumbnail_file': pic_optimize(the_file, 'WEBP'),
            'md5': file_md5(the_file)
        }
        if data.get('albumId', None):
            db_data['belong_to_album'] =  data['albumId']
        try:
            eg=NewImageSerializer(data=db_data)
            if eg.is_valid(raise_exception=True):
                eg.save()
                return Response({'msg':'图片上传成功'})
        except Exception as e:
            print(e)
            return Response({'msg':'保存图片失败'}, status=500)
    else:
        return Response({'msg':'没有检测到文件'}, status=400)

    