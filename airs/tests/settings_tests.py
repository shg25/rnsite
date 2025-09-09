"""
Djangoの設定機能のテスト
"""
from django.test import TestCase, override_settings
from unittest.mock import patch
import os


class AllowedHostsTest(TestCase):
    """ALLOWED_HOSTS動的設定のテスト"""
    
    @patch.dict(os.environ, {})
    def test_local_development_hosts(self):
        """ローカル開発環境でのALLOWED_HOSTS"""
        # settings.pyから関数をインポートして実行
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        expected_hosts = ['localhost', '127.0.0.1', '[::1]']
        
        self.assertEqual(hosts, expected_hosts)
    
    @patch.dict(os.environ, {
        'CUSTOM_DOMAIN': 'example.com'
    })
    def test_custom_domain_only(self):
        """カスタムドメインのみ設定"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        self.assertIn('example.com', hosts)
        self.assertEqual(len(hosts), 1)
    
    @patch.dict(os.environ, {
        'RAILWAY_STATIC_URL': 'https://myapp-production.railway.app'
    })
    def test_railway_static_url_only(self):
        """Railway標準URLのみ設定"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        self.assertIn('myapp-production.railway.app', hosts)
        self.assertEqual(len(hosts), 1)
    
    @patch.dict(os.environ, {
        'CUSTOM_DOMAIN': 'example.com',
        'RAILWAY_STATIC_URL': 'https://myapp-production.railway.app'
    })
    def test_multiple_domains(self):
        """複数ドメイン設定"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        self.assertIn('example.com', hosts)
        self.assertIn('myapp-production.railway.app', hosts)
        self.assertEqual(len(hosts), 2)
    
    @patch.dict(os.environ, {
        'CUSTOM_DOMAIN': 'example.com',
        'RAILWAY_STATIC_URL': 'https://example.com',  # 同じドメイン
        'RAILWAY_PUBLIC_DOMAIN': 'example.com'       # 同じドメイン
    })
    def test_duplicate_domain_removal(self):
        """重複ドメインの除去"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        # 重複が除去されて1つだけになることを確認
        self.assertEqual(hosts.count('example.com'), 1)
        self.assertEqual(len(hosts), 1)
    
    @patch.dict(os.environ, {
        'RAILWAY_STATIC_URL': 'https://myapp.railway.app',
        'RAILWAY_PUBLIC_DOMAIN': 'myapp-backup.railway.app'
    })
    def test_railway_domains_fallback(self):
        """Railway複数ドメインのフォールバック"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        self.assertIn('myapp.railway.app', hosts)
        self.assertIn('myapp-backup.railway.app', hosts)
        self.assertEqual(len(hosts), 2)
    
    @patch.dict(os.environ, {
        'RAILWAY_STATIC_URL': 'invalid-url'  # 無効なURL
    })
    def test_invalid_railway_url(self):
        """無効なRailway URLの処理"""
        from rnsite.settings import get_allowed_hosts
        
        hosts = get_allowed_hosts()
        
        # 無効なURLの場合はローカル開発環境の設定にフォールバック
        expected_hosts = ['localhost', '127.0.0.1', '[::1]']
        self.assertEqual(hosts, expected_hosts)
    
