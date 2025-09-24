# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

「raisyumo-nanitozo!!」はラジオ聴取管理システムのDjangoアプリケーションです。ユーザーがラジオ番組の聴取履歴を記録し、コメントを共有するソーシャルプラットフォームです。

## 開発コマンド

### 初回セットアップ
```bash
# 1. local_settings.py を作成（必須）
# ルートディレクトリに local_settings.py を作成し、下記「ローカル開発設定」の内容を記述

# 2. データベース初期化
python manage.py migrate
python manage.py loaddata airs/fixtures/*.json

# 3. 開発サーバー起動
python manage.py runserver
```

### 基本的なDjangoコマンド
```bash
# 開発サーバー起動
python manage.py runserver

# データベースマイグレーション
python manage.py makemigrations
python manage.py migrate

# 管理者ユーザー作成
python manage.py createsuperuser

# テスト実行
python manage.py test

# デバッグモードでテスト実行
python manage.py test --debug-mode

# 単体テスト実行例
python manage.py test airs.tests.models.air_model_tests
python manage.py test airs.tests.views.air_views_tests

# Django shell起動
python manage.py shell

# 静的ファイル収集
python manage.py collectstatic
```

### 依存関係管理
```bash
# 依存関係インストール
pip install -r requirements.txt

# pipアップデート
pip install --upgrade pip

# アップデート可能パッケージ確認
pip list -o

# 特定パッケージのアップデート
pip install -U -r requirements.txt

# パッケージ依存関係確認
pip check

# 依存関係の更新後、requirements.txt更新
pip freeze > requirements.txt
```

### Railway本番運用
```bash
# Railway CLIインストール
npm install -g @railway/cli

# Railwayログイン
railway login

# プロジェクトリンク（初回のみ）
railway link

# デプロイ
git push origin release  # 本番リリース用ブランチ
git push origin develop  # STG環境用ブランチ

# Railway環境でコマンド実行
railway run python manage.py migrate
railway run python manage.py createsuperuser

# ログ確認
railway logs           # 全ログ
railway logs -d        # デプロイログ
railway logs -b        # ビルドログ

# 環境変数管理
railway variables      # 一覧表示
railway variables set KEY=value
railway variables del KEY

# シェルアクセス
railway shell

# 手動バックアップ（重要な変更前）
railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# 環境切り替え
railway environment production  # 本番環境
railway environment staging     # STG環境
```

### バックアップシステムコマンド
```bash
# バックアップサービスのテスト実行
cd backup-service
npm test
npm run test:coverage

# 手動バックアップ実行
railway run node smart-backup.js

# バックアップサービスのデプロイ
cd backup-service
railway up
```

### Git ブランチ戦略
```bash
# ブランチ構成
develop           # 開発用ブランチ（STG環境へデプロイ）
release           # 本番リリース用ブランチ
main              # メインブランチ（安定版）

# 開発フロー
1. develop → staging環境で検証
2. develop → release（本番リリース準備）
3. release → production環境へデプロイ
4. release → main（本番リリース完了後）
```

## アプリケーションアーキテクチャ

### 主要なモデル構成
- **Air（放送）**: ラジオ番組の個別放送回を表現
- **Broadcaster（放送局）**: ラジオ局の情報
- **Program（番組）**: ラジオ番組の基本情報
- **Nanitozo（何卒/聴取）**: ユーザーの聴取記録とコメント
- **FormattedName（整形した名前）**: 名前の表記揺れを統一管理

### カスタムManager
- `AirTwoWeekListManager`: 2週間以内の放送データを取得
- `AirIdentificationManager`: 放送の識別管理
- `NanitozoListManager`: 何卒一覧の表示制御
- `NanitozoSelfListManager`: ユーザー自身の何卒管理
- `NanitozoCloseListManager`: 非公開何卒の管理

### URLルーティング
メインアプリケーション `airs` で以下の機能を提供:
- 放送一覧・詳細（`/`, `/<int:pk>/`）
- 何卒作成・更新・削除（`/<int:air_id>/nanitozo/...`）
- ユーザー・放送局・番組の一覧・詳細
- radikoシェアURL対応の放送作成機能

### テンプレート構成
- `base.html`: 基本レイアウト（UIkit使用）
- 各エンティティごとの一覧・詳細テンプレート
- カスタムテンプレートタグで日時処理や何卒表示を制御

### 設定のポイント
- 本番環境では `local_settings.py` で設定をオーバーライド
- Sentry統合でエラー監視
- 日本時間（Asia/Tokyo）でのタイムゾーン設定
- PostgreSQL使用（環境変数で認証情報管理）
- WhiteNoiseで静的ファイル配信

### Railway環境構成
- **本番環境**: production環境にデプロイ
- **STG環境**: staging環境（App Sleep活用で低コスト運用）
- **バックアップサービス**: 週1回自動実行（S3保存）

### カスタム機能
- radikoのシェアURLからの自動放送登録
- 何卒（聴取記録）の非同期作成・更新API
- 同一番組・時間での重複チェック制約
- 週間聴取パターンの分析機能
- UIkitベースのレスポンシブUI

## 開発時の注意点

### ローカル開発設定
**重要**: `local_settings.py` をルートディレクトリに作成する必要があります（.gitignore対象）:
```python
SECRET_KEY = '適当な文字列'
DEBUG = True

# ローカル開発用にSQLiteを使用（PostgreSQL依存関係の問題回避）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# テスト環境用に静的ファイルの設定を簡素化
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

### ローカル開発データベース（SQLite）
- **推奨**: PostgreSQLの代わりにSQLiteを使用
- **理由**: PostgreSQL依存関係（psycopg2）の設定が不要で環境構築が簡単
- **ファイル**: `db.sqlite3`（プロジェクト固有、他プロジェクトに影響なし）
- **初期セットアップ**:
```bash
python manage.py migrate
python manage.py loaddata airs/fixtures/*.json  # 374オブジェクトのテストデータ投入
```

### データベース制約
- Air: `broadcaster` + `started_at` の組み合わせで一意制約
- Nanitozo: `air` + `user` の組み合わせで一意制約

### 検索インデックス（名前の表記ゆれ対応）
放送局名・番組名の検索時の正規化処理:
- 小文字変換 + 半角変換 + スペース除去
- Python実装: `mojimoji.zen_to_han(文字列).lower().replace(' ', '')`

### ユーザー認証システム
- 管理サイトでユーザー手動追加（最大100人程度想定）
- `username`: ログインID（画面非表示）
- `last_name`: 表示名（大文字アルファベット3文字固定）
- `is_staff`: 管理サイトアクセス権限
- ゲストでもデータ参照可能
- メールアドレス不使用、パスワードリセット機能なし

### UIkit使用パターン
- 高さ合わせ: `.uk-flex` + `.uk-flex-middle`
- テキスト省略: `.uk-width-expand` + `.uk-text-truncate`
- ブロック要素リンク: `.uk-display-block` + `.uk-link-reset` + `.uk-animation-slide-bottom-small`
- アニメーション: `.uk-animation-toggle` + `tabindex="0"` を親要素に設定
- テキストサイズ: `.uk-text-lead`, `.uk-text-small`, `.uk-article-meta`
- 独自クラス: `.border-left-muted`, `.border-left-success`（リスト左横線）

### テスト
テストファイルは `airs/tests/` 配下に機能別に分類:
- `models/`: モデルのテスト
- `views/`: ビューのテスト
- `templatetags/`: カスタムテンプレートタグのテスト

### ログ設定
カスタムロガー `share_text` でデバッグレベルのログ出力が設定済み。

### セキュリティ
- 本番環境では `DEBUG = False`
- 環境変数で `SECRET_KEY` と `SENTRY_DSN` を管理
- CSRF保護とXFrame保護が有効
- 本番環境でHTTPS強制とセキュリティヘッダー自動付与

### 使用ライブラリ（独自選択分）
- `pytz`: タイムゾーン変換
- `beautifulsoup4`: WEBスクレイピング & HTMLパーサ
- `mojimoji`: 全角半角変換
- `urlextract`: 文字列からURL抽出

## Railway移行について

### Railway環境設定
- GitHubリポジトリから自動デプロイ
- DockerfileベースのビルドとデプロイVMで
- railway.jsonで再起動ポリシー設定

### 必要な環境変数
```
SECRET_KEY=django_secret_key
DATABASE_URL=postgresql://user:password@host:port/dbname
SENTRY_DSN=sentry_dsn_url（任意）
RAILWAY_STATIC_URL=https://your-app.railway.app（自動設定）
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app（自動設定）

# 独自ドメイン使用時に追加
CUSTOM_DOMAIN=your-custom-domain.com
```

### 独自ドメイン設定手順
```bash
# 1. Railway Dashboard > Settings > Domains
# 2. Add Custom Domain: your-custom-domain.com
# 3. DNS設定: CNAME your-custom-domain.com → your-app.railway.app
# 4. Railway環境変数に追加
railway variables set CUSTOM_DOMAIN=your-custom-domain.com

# 5. デプロイ（自動的にALLOWED_HOSTSが更新される）
git push origin release
```

### 運用強化機能（2025年9月実装）
#### 1. ヘルスチェック機能
- **エンドポイント**: `/health/`
- **機能**: データベース接続確認付きヘルスチェック
- **Railway設定**: 自動復旧、30秒タイムアウト

#### 2. セキュリティ強化
```python
# 本番環境での強化セキュリティ設定
SECURE_SSL_REDIRECT = True          # HTTPS強制リダイレクト
SESSION_COOKIE_SECURE = True        # セキュアクッキー
CSRF_COOKIE_SECURE = True          # CSRFトークン保護
SECURE_HSTS_SECONDS = 31536000     # HSTS設定
```

#### 3. セキュリティヘッダー自動付与
- **Content Security Policy (CSP)**: XSS攻撃防止
- **X-Frame-Options**: クリックジャッキング防止
- **X-Content-Type-Options**: MIMEタイプスニッフィング防止
- **Strict-Transport-Security**: HTTPS強制

#### 4. 本番ログ最適化
- **レベル**: INFO以上（DEBUGログ無効化）
- **フォーマット**: 構造化ログ（関数名・行番号付き）
- **ターゲット**: Django・airs・share_textの適切なログレベル設定

#### 5. Railway最適化設定
```json
{
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### STG環境運用方針

**標準パターン**: 完全分離型 + App Sleep活用

```bash
# STG環境の基本仕様
- 本番環境から完全分離（安全性確保）
- App Sleep自動適用（$1-3/月の低コスト運用）
- テストデータ使用（374オブジェクト）
- 月初作成・不要時削除の効率運用

# 基本的なSTG環境作成
railway environment new staging
railway environment staging
railway add postgresql
railway run python manage.py migrate
railway run python manage.py loaddata airs/fixtures/*.json
```

## 完全自動バックアップシステム（実装完了）

### システム構成
```
backup-service/
├── smart-backup.js    # メインバックアップロジック
├── cron-backup.js     # cronスケジューラー
├── Dockerfile         # コンテナ設定
└── package.json       # 依存関係
```

### 主な機能
- **週1回自動実行**: 毎週日曜5AM UTC（日本時間14時）
- **サイズ監視**: 前回比50%超の変化で Slack アラート
- **自動管理**: 古いバックアップファイル自動削除
- **AWS S3保存**: 暗号化付きクラウドストレージ
- **エラー通知**: 失敗時の自動Slack通知
- **日時ログ**: 日本時間でのログ出力

### 環境変数一覧
```bash
# 必須環境変数
DATABASE_URL=postgresql://user:pass@host:port/db  # Railway DB URL
AWS_ACCESS_KEY_ID=AKIA...                         # AWS S3アクセスキー
AWS_SECRET_ACCESS_KEY=secret...                   # AWS S3シークレット
AWS_S3_BUCKET=my-backup-bucket                    # S3バケット名

# オプション環境変数（デフォルト値あり）
AWS_S3_REGION=ap-northeast-1                      # AWS リージョン
BACKUP_SIZE_THRESHOLD=50                          # サイズ変化アラート閾値(%)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...     # Slack通知URL（任意）
BACKUP_CRON_SCHEDULE="0 5 * * 0"                 # cronスケジュール
BACKUP_PREFIX=weekly-backup                       # ファイル名プレフィックス
```