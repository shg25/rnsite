"""
セキュリティ強化のためのカスタムミドルウェア
"""

class SecurityHeadersMiddleware:
    """
    セキュリティヘッダーを追加するミドルウェア
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # セキュリティヘッダーの設定
        if not response.has_header('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        if not response.has_header('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'
        
        if not response.has_header('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        if not response.has_header('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HTTPS環境でのみSTSヘッダーを追加
        if request.is_secure():
            if not response.has_header('Strict-Transport-Security'):
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy (CSP)
        if not response.has_header('Content-Security-Policy'):
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com getuikit.com",
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com getuikit.com fonts.googleapis.com",
                "font-src 'self' fonts.gstatic.com",
                "img-src 'self' data:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'"
            ]
            response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response