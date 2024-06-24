import base64
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics
from .models import User, File
from .serializers import RegisterSerializer,LoginSerializer,UserSerializer,FileSerializer
from rest_framework.response import Response
from rest_framework import status
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework import permissions

# Create your views here.
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

class VerifyEmailAPI(APIView):
    def get(self, request, token, *args, **kwargs):
        try:
            email = base64.urlsafe_b64decode(token.encode()).decode()
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            return Response({'status': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        _, token = AuthToken.objects.create(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        })

class UploadFileAPI(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_ops_user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        file = request.Files.get('file')
        if not file.name.endswith(('.pptx', '.docx', '.xlsx')):
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)

        file_instance = File.objects.create(uploaded_by=request.user, file=file)
        return Response({"file": FileSerializer(file_instance).data}, status=status.HTTP_201_CREATED)

class ListFilesAPI(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.all()

class DownloadFileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id, *args, **kwargs):
        file = File.objects.get(id=file_id)
        if not file:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        
        response = HttpResponse(file.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response