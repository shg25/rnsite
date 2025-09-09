"""
ヘルスチェック機能のテスト
"""
from django.test import TestCase, Client
from django.db import connection
from unittest.mock import patch, MagicMock
import json


class HealthCheckViewTest(TestCase):
    """ヘルスチェックエンドポイントのテスト"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_success(self):
        """正常なヘルスチェック"""
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
        self.assertEqual(data['service'], 'rnsite')
    
    def test_health_check_cache_headers(self):
        """キャッシュ無効化の確認"""
        response = self.client.get('/health/')
        
        # Cache-Controlヘッダーでキャッシュが無効化されていることを確認
        self.assertIn('no-cache', response.get('Cache-Control', '').lower())
    
    @patch('airs.health_views.connection')
    def test_health_check_database_failure(self, mock_connection):
        """データベース接続失敗時の動作"""
        # データベースエラーをシミュレート
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('Database connection failed')
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['database'], 'disconnected')
        self.assertIn('error', data)
        self.assertEqual(data['service'], 'rnsite')
    
    def test_health_check_method_not_allowed(self):
        """GET以外のHTTPメソッドでのアクセス"""
        response = self.client.post('/health/')
        self.assertEqual(response.status_code, 405)
        
        response = self.client.put('/health/')
        self.assertEqual(response.status_code, 405)
        
        response = self.client.delete('/health/')
        self.assertEqual(response.status_code, 405)