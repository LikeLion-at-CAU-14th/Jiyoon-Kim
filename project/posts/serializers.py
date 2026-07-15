### Model Serializer case

from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import *

from config.custom_api_exceptions import *
from django.utils import timezone

class PostSerializer(serializers.ModelSerializer):

  class Meta:
    model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
    fields = ["title", "content", "status", "writer"] # 모델에서 어떤 필드를 가져올지 >> 전체 필드
    
  def validate(self, data):

    # 중복된 게시글 제목이 있다면 예외 발생
    if Post.objects.filter(title=data['title']).exists():
      raise PostConflictException(detail=f"A post with title: '{data['title']}' already exists.")
    
    # 게시글 작성자가 하루에 하나의 게시글만 업로드할 수 있도록 제한
    today = timezone.now().date()
    if not self.instance: # 새 게시글 생성 시에만 검사
      if Post.objects.filter(writer=data['writer'], created_at__date=today).exists():
        raise DailyPostLimitException(detail="You can only upload one post per day.")

    return data

class CommentSerializer(serializers.ModelSerializer):

  class Meta:
    model = Comment
    fields = "__all__"

# 댓글 content 필드 최소 길이 검증
  def validate_content(self, value):
    if len(value) < 15:
      raise CommentMinimumLengthException( detail="The provided comment does not meet the minimum length requirement of 15 characters.")
    return value


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"