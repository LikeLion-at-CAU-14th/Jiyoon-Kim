from django.contrib import admin
from .models import Post, Comment, Category

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'writer', 'get_categories', 'created_at', 'updated_at')

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    get_categories.short_description = 'Categories'
    
admin.site.register(Post, PostAdmin)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'writer', 'post', 'created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')