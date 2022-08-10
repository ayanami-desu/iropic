from django.http import JsonResponse, FileResponse, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .serializers import *
from .models import Images, Labels, Albums, upload_file_deleted
from .optimize import pic_optimize
import hashlib
import random

def file_md5(web_file):
    data = web_file.open(mode='rb').read()
    return hashlib.md5(data).hexdigest()

class Tool(APIView):
    def get(self, request):
        return JsonResponse({'msg':'操作完成'})
    def post(self, request):
        return JsonResponse({'msg':'操作完成'})

@api_view(['GET'])
def random_image(request):
    field = request.GET.get('field', None)
    if field == None:
        return Response({'msg': '参数无效'}, status=400)
    max_id = Images.objects.last().id
    min_id = Images.objects.first().id
    times = 0
    while times<200:
        pk = random.randint(min_id, max_id)
        image = Images.objects.filter(pk=pk).first()
        times += 1
        if image:
            break
    if field == 'image':
        return HttpResponse(image.webp_file, content_type="image/webp")
    if field == 'pid':
        return Response({'pid': image.id})

class ImageApi(APIView):
    #根据图片id返回图片
    def get(self, request):
        file_type = request.GET.get('fileType', 'webp')
        #支持的文件格式，jpeg,webp,origin
        try:
            pid = request.GET['pid']
            image = Images.objects.get(id=pid)
            if file_type == 'webp':
                #不带参数，或参数为webp均返回webp缩略图
                return FileResponse(image.webp_file)
            elif file_type == 'origin':
                #返回原图
                return FileResponse(image.origin_file)
            else:
                return Response({'msg':'不支持的文件类型'}, status=400)
        except Exception as e:
            print(e)
            return Response({'err':str(e)}, status=500)
    def post(self, request):
        #获取图片对象，以列表形式返回
        try:
            page = int(request.data.get('page', -1))
            num = int(request.data.get('num', -1))
            sort_by = request.data.get('sortBy', 'down')
            if num>16:
                return Response({'msg':'超过一次请求限制最大数量'}, status=400)
            if page<0 or num<0:
                return Response({'msg': '页码或数量无效'}, status=400)
            album_id = request.data.get('albumId', None)
            tags = request.data.get('tags', None)
            mode = request.data.get('mode', 'or')
            images = Images.objects.filter(p_image=None)
            if not request.auth:
                images = images.exclude(isR18=True)
            if album_id:
                images = images.filter(belong_album=album_id)
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
            data = ImageListSer(images, many=True).data
            return Response({'data':data, 'imageNum':images_num})
        except Exception as e:
            print(e)
            return Response({'err':str(e)}, status=500)
    def delete(self, request):
        #删除图片
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
    def put(self, request):
        #将多张图片设为一组，以pidList中第一个pid为组id。
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pidList = request.data.get('pidList', None)
        if pidList == None:
            return Response({'msg': '无效参数'}, status=400)
        list_len = len(pidList)
        if list_len<2:
            return Response({'err': '提供的图片数量应大于等于2'}, status=400)
        try:
            p_img = Images.objects.get(id=pidList[0])
            for i in range(1, list_len):
                img  = Images.objects.get(id=pidList[i])
                img.p_image = p_img
                img.save()
            return Response({'msg':'合并完成'})
        except Exception as e:
            print(e)
            return Response({'err':str(e)}, status=500)

class ImageData(APIView):
    def get(self, request):
        #获取图片的全部信息
        pid = request.GET.get('pid', None)
        if pid == None:
            return Response({'msg': '无效参数'}, status=400)
        try:
            image = Images.objects.get(id=pid)
            image_data = ImageInfoSer(image).data
            # img_files = image.imagefile_set.all()
            # size_list = []
            # for f in img_files:
            #     size_list.append(f.origin_file.size)
            return Response({'data':image_data})
        except Exception as e:
            print(e)
            return Response({'msg':'获取图片信息失败','err':str(e)}, status=500)    
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
        img_data = {
            'origin_file': the_file,
            'edit_time': data['lastModified'],
            'origin_filename': data['name'],
            'file_type': data['fileType'],
            'webp_file': pic_optimize(the_file, 'WEBP'),
            'md5': file_md5(the_file)
        }
        if data.get('albumId', None):
           img_data['belong_album'] =  data['albumId']
        try:
            image = NewImageSer(data=img_data)
            if image.is_valid(raise_exception=True):
                image.save()
                return Response({'msg':'图片上传成功'})
        except Exception as e:
            print(e)
            return Response({'msg':'保存图片失败', 'err': str(e)}, status=500)
    else:
        return Response({'msg':'没有检测到文件'}, status=400)

    