import logging

logger = logging.getLogger('django.request.custom')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 요청 로깅
        logger.info(f"요청 URL: {request.path} | Method: {request.method}")
        
        response = self.get_response(request)
        
        # 응답 상태코드가 400 이상이면 warning으로 로깅
        if response.status_code >= 400:
            logger.warning(
                f"에러 응답 | URL: {request.path} | Status: {response.status_code}"
            )
        
        return response