from rest_framework.response import Response
from rest_framework.views import APIView

class LoginApi(APIView):
    def get(self, request):
        if request.auth:
            return Response({'msg':'已登录', 'code':1})
        else:
            return Response({'msg':'未登录', 'code':0}, status=401)