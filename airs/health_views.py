"""
Railway用ヘルスチェック機能
"""
import logging
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """
    Railway向けヘルスチェックエンドポイント
    データベース接続確認を含む簡易ヘルスチェック
    """
    try:
        # データベース接続確認
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({
            "status": "healthy",
            "database": "connected",
            "service": "rnsite"
        }, status=200)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e),
            "service": "rnsite"
        }, status=503)