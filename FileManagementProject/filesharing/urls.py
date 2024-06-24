from django.urls import path
from .views import RegisterAPI,VerifyEmailAPI,ListFilesAPI,LoginAPI,UploadFileAPI,DownloadFileAPI 


urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify-email/<str:token>/', VerifyEmailAPI.as_view(), name='verify-email'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('upload-file/', UploadFileAPI.as_view(), name='upload-file'),
    path('files/', ListFilesAPI.as_view(), name='list-files'),
    path('files/<int:file_id>/', DownloadFileAPI.as_view(), name='download-file'),
]
