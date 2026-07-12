from django.contrib import admin
from django.urls import path, include
from posts.views import *

urlpatterns = [
    #path('', hello_world, name = 'hello_world'),
    #path('page', index, name='my-page'),
    #path('<int:id>', get_post_detail),
    #path('<int:post_id>/', PostDetail.as_view()),

    #path('', post_list, name = "post_list"), # Post 생성, 전체조회
    #path('<int:post_id>/', post_detail, name = "post_detail"), # Post 단일조회, 수정, 삭제
    #path('<int:post_id>/comments/', get_post_comments, name = "post_comments") # Post의 댓글 조회

    path('', PostList.as_view()), # post 전체 조회
    path('<int:post_id>/', PostDetail.as_view()), # post 개별 조회
    # path('<int:post_id>/comments/', CommentList.as_view()), # post의 댓글 조회, 생성
    # path('comments/<int:comment_id>/', CommentDetail.as_view()), # post의 댓글 삭제
    # path('upload/', ImageUploadView.as_view(), name='image-upload')
]