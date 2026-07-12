
class BaseCustomException(Exception):
    default_detail = "An error occurred"
    default_code = "ERROR"
    status_code = 500
    
    def __init__(self, detail=None, code=None):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        super().__init__(self.detail)


# 리소스가 없는 상황에 대한 기본 예외 클래스
class ResourceNotFoundException(BaseCustomException):
    default_detail = "The requested resource was not found."
    default_code = "RESOURCE-NOT-FOUND"
    status_code = 404

class PostNotFoundException(ResourceNotFoundException):
    default_detail = "Post not found with the given ID."
    default_code = "POST-NOT-FOUND"