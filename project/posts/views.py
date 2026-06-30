from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import *

import json


### DRF 관련 import - APIView 사용
from .serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from rest_framework.permissions import IsAuthenticatedOrReadOnly # jwt 세션
from config.permissions import IsAllowedTime, IsOwnerOrReadOnly  #custom permissions

from django.core.files.storage import default_storage  
from .serializers import ImageSerializer
from django.conf import settings
import boto3

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import uuid
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.

# FBV - 함수 기반 뷰
"""
# 게시글 단일조회(GET), 수정(PATCH) 로직, 삭제(DELETE) 로직
@require_http_methods(["GET","PATCH","DELETE"])
def post_detail(request, post_id):
    
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id) # post_id 에 해당하는 Post 데이터 가져오기
    
        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "writer" : post.writer.username
        }
        return JsonResponse({
            "status" : 200,
            'message' : '게시글 단일 조회 성공',
            "data": post_detail_json})
    
    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))

        post_update = get_object_or_404(Post, pk=post_id)

        if 'title' in body:
            post_update.title = body['title']
        if 'content' in body:
            post_update.content = body['content']
        if 'status' in body:
            post_update.status = body['status']
        
        post_update.save()

        post_update_json = {
            "id" : post_update.id,
            "title" : post_update.title,
            "content" : post_update.content,
            "status" : post_update.status,
            "writer" : post_update.writer.username
        }

        return JsonResponse({
            'status': 200,
            'message' : '게시글 수정 성공',
            'data' : post_update_json
        })
    
    if request.method == "DELETE":
        post_delete = get_object_or_404(Post, pk=post_id)
        post_delete.delete()

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 삭제 성공',
            'data' : None
        })


@require_http_methods(["GET"])
def get_post_detail(request, id):
    post = get_object_or_404(
    Post.objects.prefetch_related('comments__writer'), # prefetch_related -> N+1 문제 해결.
    pk=id
)
    post_detail_json = {
        "id" : post.id,
        "title" : post.title,
        "content" : post.content,
        "status" : post.status,
        "writer" : post.writer.username,
        "categories": [c.name for c in post.categories.all()],
        "comments": [
            {
                "writer": c.writer.username,
                "content": c.content
            }
            for c in post.comments.all()
             ],
             
        "created_at" : post.created_at,
        "updated_at" : post.updated_at
    }
    return JsonResponse({
        "status" : 200,
        "data": post_detail_json})


# 게시글을 Post(Create), Get(Read) 하는 뷰 로직
@require_http_methods(["POST", "GET"])   #함수 데코레이터, 특정 http method 만 허용합니다
def post_list(request):

    if request.method == "POST":

        # request.body의 byte -> 문자열 -> python 딕셔너리
        body = json.loads(request.body.decode('utf-8'))

        # 프론트에게서 user id를 넘겨받는다고 가정.
				# 외래키 필드의 경우, 객체 자체를 전달해줘야하기 때문에
        # id를 기반으로 user 객체를 조회해서 가져옵니다 !
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)

        # 새로운 데이터를 DB에 생성
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            writer = user
        )

        # Json 형태 반환 데이터 생성
        new_post_json = {
            "id" : new_post.id,
            "title" : new_post.title,
            "content" : new_post.content,
            "status" : new_post.status,
            "writer" : new_post.writer.username
        }

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 생성 성공',
            'data' : new_post_json
        })

 # 게시글 전체 조회
    if request.method == "GET":
        posts = Post.objects.all()

        #  카테고리 필터링
        category_id = request.GET.get('category')
        if category_id:
            posts = posts.filter(categories__id = category_id)
        
        # 정렬 (최신 작성 순- latest) - 항상.
        posts = posts.order_by('-created_at')


        # 각 데이터를 Json 형식으로 변환하여 리스트에 저장 (여러개의 게시글 내용을 담을 거라 리스트를 이용합니다)
        post_all_json = []

        for post in posts:
            post_json = {
                "id" : post.id,
                "title" : post.title,
                "categories": [c.name for c in post.categories.all()],
                "content" : post.content,
                "status" : post.status,
                "writer" : post.writer.username,
                "created_at": post.created_at
            }
            post_all_json.append(post_json)

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 목록 조회 성공',
            'data' : post_all_json
        })
    
# 특정 게시글의 모든 댓글 조회
@require_http_methods(["GET"])
def get_post_comments(request, post_id):
    post = get_object_or_404(
        Post.objects.prefetch_related('comments__writer'), pk=post_id) # prefetch_related -> N+1 문제 해결.
    comments = post.comments.all()

    comments_json = [
        {
            "writer": comment.writer.username,
            "content": comment.content,
            "created_at": comment.created_at
        }
        for comment in comments
    ]

    return JsonResponse({
        "status": 200,
        'message' : '게시글 댓글 조회 성공',
        "data": comments_json
    })
"""
# CBV - 클래스 기반 뷰
### DRF - APIView 사용

class PostList(APIView):

    permission_classes = [IsAllowedTime, IsOwnerOrReadOnly]

    @swagger_auto_schema(
            operation_summary="게시글 생성",
            operation_description="새로운 게시글을 생성합니다.",
            request_body=PostSerializer,  # 요청 데이터의 스키마 정의
            responses={201: PostSerializer, 400: "잘못된 요청"},  # 응답 데이터의 스키마 정의
    )

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostDetail(APIView):
   # permission_classes = [IsAuthenticatedOrReadOnly]
   permission_classes = [IsAllowedTime, IsOwnerOrReadOnly]
   
   @swagger_auto_schema(
        operation_summary="게시글 상세 조회",
        operation_description="특정 게시글의 상세 정보를 조회합니다.",
        responses={200: PostSerializer}
    )
    
   def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
   
   @swagger_auto_schema(
        operation_summary="게시글 수정",
        operation_description="특정 게시글을 수정합니다.",
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "잘못된 요청"}
    )

   def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)    # 수정 권한 체크
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():   # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   @swagger_auto_schema(
        operation_summary="게시글 삭제",
        operation_description="특정 게시글을 삭제합니다.",
        responses={200: "게시글 삭제 성공"}
    )
   def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(request, post)   # 삭제 권한 체크
        post.delete()
        return Response(
            {
                "message": "게시글이 성공적으로 삭제되었습니다.",
                "post_id": post_id
            },
            status=status.HTTP_200_OK
        )
    
# 댓글 생성, 조회
class CommentList(APIView):

    # permission_classes = [IsAllowedTime, IsOwnerOrReadOnly]
    @swagger_auto_schema(
        operation_summary="댓글 생성",
        operation_description="특정 게시글에 댓글을 생성합니다.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "잘못된 요청"}
    )

		# 게시글에 댓글 생성 (POST)
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = request.data.get('writer')
            user = get_object_or_404(User, pk=user_id)
            serializer.save(writer=user, post=post)
            return Response({
                "status": 201,
                "message": "댓글 생성 성공",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="댓글 조회",
        operation_description="특정 게시글의 모든 댓글을 조회합니다.",
        responses={200: CommentSerializer}
    )

    # 게시글의 모든 댓글 조회 (GET)
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.all().prefetch_related('writer')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "status": 200,
            "message": "게시글 댓글 조회 성공",
            "data": serializer.data
        })
    

# 댓글 삭제
class CommentDetail(APIView):
    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        operation_description="특정 댓글을 삭제합니다.",
        responses={200: "댓글 삭제 성공"}
    )
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.delete()
        return Response({
            "status": 200,
            "message": "댓글 삭제 성공",
            "data": None
            }, status=status.HTTP_200_OK)
    


class ImageUploadView(APIView):

    # permission_classes = [IsAuthenticatedOrReadOnly]

    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="이미지 업로드",
        operation_description="이미지를 업로드하고 S3에 저장합니다.",
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM, description="Upload a file",
                type=openapi.TYPE_FILE, required=True),
        ],

        responses={201: ImageSerializer, 400: "잘못된 요청"}
    )
    
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        # S3에 파일 저장
        unique_filename = f"{uuid.uuid4()}_{image_file.name}"
        file_path = f"uploads/{unique_filename}"
        # S3에 파일 업로드
        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=image_file.content_type,
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 업로드된 파일의 URL 생성
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        
        # DB에 저장
        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)


        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


