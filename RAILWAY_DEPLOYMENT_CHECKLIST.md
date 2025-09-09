# Railway デプロイ後動作確認チェックリスト

## 🚀 デプロイ前の準備

### 1. ローカルテスト実行
```bash
# すべてのテストを実行
python manage.py test

# 新規追加したテストを実行
python manage.py test airs.tests.views.health_views_tests
python manage.py test airs.tests.settings_tests
python manage.py test airs.tests.middleware_tests

# テスト実行結果の確認例
# Ran XX tests in X.XXXs
# OK (expected)
```

### 2. 環境変数設定確認
```bash
# Railway環境変数の設定確認
railway variables

# 必須環境変数チェックリスト
# ✅ SECRET_KEY=xxxxx
# ✅ DATABASE_URL=postgresql://xxxxx
# ✅ SENTRY_DSN=https://xxxxx (任意)
# ✅ CUSTOM_DOMAIN=your-domain.com (独自ドメイン使用時)
```

## 🔍 デプロイ後の動作確認

### 1. ヘルスチェック機能の確認

#### A. 基本動作確認
```bash
# ヘルスチェックエンドポイントにアクセス
curl -v https://your-app.railway.app/health/

# 期待されるレスポンス例
# HTTP/1.1 200 OK
# Content-Type: application/json
# Cache-Control: no-cache, no-store, must-revalidate
#
# {
#   "status": "healthy",
#   "database": "connected", 
#   "service": "rnsite"
# }
```

#### B. Railway自動監視の確認
```bash
# Railway Dashboard > Service > Health Checks でステータス確認
# ✅ Health check: Passing
# ✅ Path: /health/
# ✅ Timeout: 30s
```

### 2. セキュリティヘッダーの確認

#### A. 基本セキュリティヘッダー
```bash
# メインページでセキュリティヘッダーを確認
curl -I https://your-app.railway.app/

# 確認すべきヘッダー
# ✅ X-Content-Type-Options: nosniff
# ✅ X-Frame-Options: DENY
# ✅ X-XSS-Protection: 1; mode=block
# ✅ Referrer-Policy: strict-origin-when-cross-origin
# ✅ Content-Security-Policy: default-src 'self'; script-src...
# ✅ Strict-Transport-Security: max-age=31536000; includeSubDomains (HTTPS時)
```

#### B. オンラインセキュリティチェック
```bash
# セキュリティヘッダー自動チェック（推奨）
# https://securityheaders.com/ で your-app.railway.app をスキャン

# 期待されるグレード: A または A+
```

### 3. ALLOWED_HOSTS設定の確認

#### A. 正常なドメインアクセス
```bash
# 設定済みドメインでのアクセステスト
curl -H "Host: your-app.railway.app" https://your-app.railway.app/
# ➜ 200 OK (正常)

# 独自ドメイン使用時
curl -H "Host: your-custom-domain.com" https://your-custom-domain.com/  
# ➜ 200 OK (正常)
```

#### B. 不正なドメインのブロック確認
```bash
# 不正なHostヘッダーでのアクセステスト
curl -H "Host: malicious-domain.com" https://your-app.railway.app/
# ➜ 400 Bad Request (期待される動作)
```

### 4. HTTPS強制設定の確認

```bash
# HTTP → HTTPS リダイレクトの確認
curl -I http://your-app.railway.app/
# ➜ 301 Moved Permanently
# ➜ Location: https://your-app.railway.app/

# HTTPS接続の確認
curl -I https://your-app.railway.app/
# ➜ 200 OK
```

### 5. ログ出力レベルの確認

```bash
# Railway本番ログの確認
railway logs

# 確認ポイント
# ✅ DEBUGレベルログが出力されていない
# ✅ INFOレベル以上のログが構造化されている
# ✅ エラーがSentryに送信されている（Sentry設定時）

# 本番ログフォーマット例
# 2025-09-09 05:00:00 [INFO] airs.views.air_views.AirListView:25 - User accessed air list
```

## 📊 パフォーマンス・可用性の確認

### 1. Railway設定の確認
```bash
# railway.json設定の動作確認
railway ps

# 確認ポイント
# ✅ Workers: 2プロセス
# ✅ Memory Usage: 適切範囲内
# ✅ Health Check: Passing
# ✅ Restart Policy: ON_FAILURE (最大10回)
```

### 2. データベース接続の確認
```bash
# Railway PostgreSQL接続テスト
railway connect

# Django shellでのDB接続テスト
railway run python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database connection: OK")
```

### 3. 静的ファイル配信の確認
```bash
# 静的ファイルアクセステスト
curl -I https://your-app.railway.app/static/airs/css/style.css
# ➜ 200 OK
# ➜ Content-Encoding: gzip (WhiteNoise圧縮確認)
# ➜ Cache-Control: max-age=60 (キャッシュ設定確認)
```

## 🚨 問題発生時のトラブルシューティング

### よくある問題と対処法

| 問題 | 症状 | 対処法 |
|------|------|--------|
| ヘルスチェック失敗 | 503エラー | `railway logs`でDB接続エラーを確認 |
| セキュリティヘッダー無し | ヘッダー不在 | ミドルウェアの設定順序を確認 |
| ALLOWED_HOSTS エラー | 400 Bad Request | 環境変数`CUSTOM_DOMAIN`を確認 |
| HTTPS設定無効 | HTTPアクセス可能 | `SECURE_SSL_REDIRECT`設定を確認 |
| 静的ファイル404 | CSS/JS読み込み失敗 | `python manage.py collectstatic`実行 |

### デバッグ用コマンド
```bash
# 設定値の確認
railway run python manage.py shell
>>> from django.conf import settings
>>> print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
>>> print("DEBUG:", settings.DEBUG)
>>> print("SECURE_SSL_REDIRECT:", settings.SECURE_SSL_REDIRECT)

# 環境変数の確認
railway run env | grep -E "(SECRET_KEY|DATABASE_URL|CUSTOM_DOMAIN)"
```

## ✅ 完了チェックリスト

- [ ] ローカルでのテスト実行（全てパス）
- [ ] Railway環境変数設定完了
- [ ] ヘルスチェックエンドポイント正常動作
- [ ] セキュリティヘッダー全て設定済み
- [ ] ALLOWED_HOSTS正常動作（不正ドメインブロック）
- [ ] HTTPS強制リダイレクト動作
- [ ] ログレベル最適化確認
- [ ] Railway設定（workers, healthcheck）動作
- [ ] データベース接続正常
- [ ] 静的ファイル配信正常
- [ ] セキュリティチェッカーでA評価以上

---

📝 **更新日**: 2025年9月9日  
🎯 **対象**: Railway migration branch  
✅ **テスト済み**: Django test suite + 手動確認