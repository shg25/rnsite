"""
セキュリティミドルウェアのテスト
"""
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import MagicMock
from airs.middleware import SecurityHeadersMiddleware


class SecurityHeadersMiddlewareTest(TestCase):
    """セキュリティヘッダーミドルウェアのテスト"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(self._mock_get_response)
    
    def _mock_get_response(self, request):
        """モックレスポンス生成"""
        return HttpResponse('Test response')
    
    def test_basic_security_headers(self):
        """基本的なセキュリティヘッダーの付与"""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        # 基本セキュリティヘッダーの確認
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
    
    def test_csp_header(self):
        """Content Security Policyヘッダーの設定"""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        csp = response['Content-Security-Policy']
        
        # CSPディレクティブの確認
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self' 'unsafe-inline'", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("base-uri 'self'", csp)
        self.assertIn("form-action 'self'", csp)
    
    def test_https_only_headers(self):
        """HTTPS環境でのみ適用されるヘッダー"""
        # HTTP環境でのテスト
        request = self.factory.get('/')
        response = self.middleware(request)
        
        # STSヘッダーはHTTP環境では設定されない
        self.assertFalse(response.has_header('Strict-Transport-Security'))
        
        # HTTPS環境をシミュレート
        request.META['wsgi.url_scheme'] = 'https'
        https_middleware = SecurityHeadersMiddleware(self._mock_get_response)
        
        # request.is_secure()をTrueにするためのモック設定
        request.is_secure = MagicMock(return_value=True)
        
        response = https_middleware(request)
        
        # HTTPS環境ではSTSヘッダーが設定される
        self.assertEqual(
            response['Strict-Transport-Security'], 
            'max-age=31536000; includeSubDomains'
        )
    
    def test_existing_headers_not_overridden(self):
        """既存ヘッダーは上書きしない"""
        # カスタムレスポンスを作成
        def custom_get_response(request):
            response = HttpResponse('Custom response')
            response['X-Frame-Options'] = 'SAMEORIGIN'  # 既存ヘッダー
            response['Content-Security-Policy'] = 'default-src none'  # 既存CSP
            return response
        
        middleware = SecurityHeadersMiddleware(custom_get_response)
        request = self.factory.get('/')
        response = middleware(request)
        
        # 既存ヘッダーが保持されることを確認
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(response['Content-Security-Policy'], 'default-src none')
        
        # 他のヘッダーは追加される
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
    
    def test_all_http_methods(self):
        """全HTTPメソッドでヘッダーが設定される"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        
        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())('/')
                response = self.middleware(request)
                
                self.assertTrue(response.has_header('X-Content-Type-Options'))
                self.assertTrue(response.has_header('X-Frame-Options'))
    
    def test_csp_external_resources(self):
        """CSPでの外部リソース許可設定"""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        csp = response['Content-Security-Policy']
        
        # UIkit CDNの許可確認
        self.assertIn('cdn.jsdelivr.net', csp)
        self.assertIn('cdnjs.cloudflare.com', csp)
        self.assertIn('getuikit.com', csp)
        
        # Google Fonts の許可確認
        self.assertIn('fonts.googleapis.com', csp)
        self.assertIn('fonts.gstatic.com', csp)