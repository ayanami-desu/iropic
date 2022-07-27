from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .models import Labels

class LabelApi(APIView):
    def get(self, request):
        #获得现在所有的标签
        keyword = request.GET.get('keyword', None)
        if keyword:
            all_label = Labels.objects.filter(name__istartswith=keyword)
        else:
            all_label = Labels.objects.all()
        data = LabelSerializer(all_label, many=True).data
        return Response({'data':data})
    def post(self, request):
        #增加标签，可一次性增加多个，以逗号分隔
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        label_string = request.data['labels']
        label_list = label_string.split(',')
        for i in range(len(label_list)):
            label = Labels(name=label_list[i])
            label.save()
        return Response({'msg':'添加完成'})
    def delete(self, request):
        #删除标签
        if not request.auth:
            return Response({'msg':'permission denied'}, status=401)
        try:
            name = request.data['name']
            label = Labels.objects.get(name=name)
            label.delete()
            return Response({'msg':'删除完成'})
        except Exception as e:
            print(e)
            return Response({'err': str(e)}, status=400)