from django.shortcuts import render
from django.http import JsonResponse 
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import *

# Create your views here.
@require_http_methods(["GET"])
def get_post_detail(reqeuest, id):
    post = get_object_or_404(Post, pk=id)
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