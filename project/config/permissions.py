from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import datetime

class IsAllowedTime(BasePermission):
    
    def has_permission(self, request, view):
        hour = datetime.now().hour
        print("현재 시간:", hour)
        if 22 <= hour or hour < 7:        # 밤 10시 ~ 아침 7시 사용 권한 제한
            return False
        return True
        
class IsOwnerOrReadOnly(BasePermission):
    
    # 비인증(로그인X) 사용자는 읽기만 가능
    def has_permission(self, request, view):
		    # 읽기 - 모두 허용
        if request.method in SAFE_METHODS:  
            return True
        # 쓰기(수정, 삭제,...) - 로그인한 사용자만
        return request.user and request.user.is_authenticated

		# 인증된(로그인O) 사용자 중 작성자만 수정
    def has_object_permission(self, request, view, obj):
        # 읽기는 모두 허용
        if request.method in SAFE_METHODS:
            return True
        # 수정/삭제는 작성자만
        return obj.writer == request.user