### Model Serializer case

from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import *

from config.custom_api_exceptions import PostConflictException

class PostSerializer(serializers.ModelSerializer):

  class Meta:
    model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
    fields = ["title", "content", "status", "writer"] # 모델에서 어떤 필드를 가져올지 >> 전체 필드
    

   # 중복된 게시글 제목이 있다면 예외 발생
  def validate(self, data):
    if Post.objects.filter(title=data['title']).exists():
      raise PostConflictException(detail=f"A post with title: '{data['title']}' already exists.")
    
    return data

class CommentSerializer(serializers.ModelSerializer):

  class Meta:
    model = Comment
    fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"