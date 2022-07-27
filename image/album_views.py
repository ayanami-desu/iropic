from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import Images, Albums

class AlbumApi(APIView):
    def get(self, request):
        #获取相册列表
        albums = Albums.objects.all()
        data = AlbumListSerializer(albums, many=True).data
        return Response({'data':data})
    def post(self,request):
        #新建相册
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        try:
            album=NewAlbumSerializer(data=request.data)
            if album.is_valid(raise_exception=True):
                album.save()
                return Response({'msg':'新建相册成功'})
        except Exception as e:
            print(e)
            return Response({'msg':'新建相册失败'}, status=400)
        
    def delete(self, request):
        #删除相册
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        album_id = request.data.get('albumId', None)
        if album_id:
            try:
                album = Albums.objects.get(id=album_id)
                album.delete()
                return Response({'msg': '删除相册成功'})
            except Exception as e:
                print(e)
                return Response({'err':str(e)}, status=401)
        else:
            return Response({'msg': '无效参数'}, status=400)
    def put(self, request):
        #修改相册信息
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        album_id = request.data.get('albumId', None)
        if album_id:
            album = Albums.objects.get(id=album_id)
            new_album = NewAlbumSerializer(album, data=request.data)
            if new_album.is_valid(raise_exception=True):
                new_album.save()
            return Response({'msg': '修改相册成功'})
        else:
            return Response({'msg': '无效参数'}, status=400)

class AlbumData(APIView):
    def post(self, request):
        #为相册增加图片
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid_list = request.data.get('pidList', None)
        album_id = request.data.get('albumId', None)
        if pid_list and album_id:
            album = Albums.objects.get(id=album_id)
            for pid in pid_list:
                image = Images.objects.get(id=pid)
                image.belong_to_album = album
                image.save()
            return Response({'msg': '添加成功'})
        else:
            return Response({'msg': '无效参数'}, status=400)
    def put(self, request):
        #为相册删除图片
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid = request.data.get('pid', None)
        album_id = request.data.get('albumId', None)
        if pid and album_id:
            image = Images.objects.get(id=pid)
            image.belong_to_album = None
            image.save()
            return Response({'msg': '删除成功'})
        else:
            return Response({'msg': '无效参数'}, status=400)

class AlbumCover(APIView):
    def get(self, request):
        #相册封面，均为缩略图，若无设置封面，默认取最新一张；有则返回设置的封面
        album_id = request.GET.get('albumId', None)
        if album_id:
            try:
                album = Albums.objects.get(id=album_id)
                if album.cover:
                    return FileResponse(album.cover)
                else:
                    images = album.images_set
                    if not images.exists():
                        return Response({'msg': '此相册无封面'}, status=404)
                    else:
                        cover = images.order_by('-edit_time')[0].thumbnail_file
                        return FileResponse(cover)
            except Exception as e:
                print(e)
                return Response({'err':str(e)}, status=401)
        else:
            return Response({'msg': '无效参数'}, status=400)
    def put(self, request):
        #修改相册封面
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        pid = request.data.get('pid', None)
        #album_id = request.data.get('albumId', None)
        if pid:
            try:
                image = Images.objects.get(id=pid)
                album = image.belong_to_album
                if album:
                    album.cover = image.thumbnail_file
                    album.save()
                    return Response({'msg':'修改相册封面成功'})
                else:
                   return Response({'msg': '此图片不属于任何相册'})
            except Exception as e:
                print(e)
                return Response({'err':str(e)}, status=401)
        else:
            return Response({'msg': '无效参数'}, status=400)