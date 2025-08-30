# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

これは「raisyumo-nanitozo!!」というラジオ聴取管理システムのDjangoアプリケーションです。ユーザーがラジオ番組の聴取履歴を記録し、コメントを共有するソーシャルプラットフォームです。

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
git push origin railway-migration  # または main

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

# Railway自動バックアップテンプレート（推奨）
# https://railway.app/template/XV2dlg
# 毎日5AM UTCで自動バックアップ（S3設定が必要）
```

### STG環境運用ガイド
```bash
# STG環境セットアップ（初回のみ）
railway environment new staging         # staging環境作成
railway environment staging            # staging環境に切り替え
# Railway Dashboard > Settings > Environments > staging > Duplicate from production

# STG環境デプロイ
railway environment staging            # staging環境に切り替え
git push origin develop               # developブランチをstaging環境にデプロイ

# STG環境確認
railway environment staging
railway variables                     # STG環境固有の環境変数確認
railway logs -d                      # STGデプロイログ確認
railway shell                        # STG環境でのシェルアクセス

# STG → 本番環境移行フロー
1. developブランチで開発 → STG環境でテスト
2. STG環境で動作確認完了
3. main/masterブランチにマージ
4. production環境へデプロイ

# STG環境データ管理
railway environment staging
railway run python manage.py loaddata airs/fixtures/*.json  # テストデータ投入
railway run python manage.py migrate                       # DB migration
```

### Railway運用チェックリスト
```bash
# 月次確認事項
1. コスト監視: Railway Dashboardでusage確認（本番+STG）
2. ログ確認: `railway logs`でエラーチェック（各環境）
3. データベース状況: 接続数、サイズ確認
4. バックアップ状況: S3バケット確認（設定済みの場合）

# 緊急時対応
railway rollback     # 前バージョンに戻す
railway restart      # サービス再起動

# 環境切り替えコマンド
railway environment production  # 本番環境
railway environment staging     # STG環境
```

### STG/本番環境の使い分け指針
```bash
# STG環境の目的
- 新機能の動作確認
- DB migrationの事前テスト  
- 本番環境に影響を与えない実験
- 外部API連携のテスト

# データ管理方針
- STG: テストデータ（fixturesファイル使用）
- 本番: 実データ（本番運用データ）

# コスト最適化戦略
- STG環境は小容量のPostgreSQLインスタンス使用
- App Sleep自動機能活用（10分非アクティブで自動スリープ）
- 長期間未使用時：環境削除で最大コスト削減

# STG環境のコスト管理
```bash
# パターン1: 自動スリープ（推奨）
# 設定不要・10分非アクティブで自動スリープ
# アクセス時に自動復帰・データ保持

# パターン2: 一時的サービス削除
railway environment staging
# Railway Dashboard > web service > Delete（DBは維持）

# パターン3: 環境完全削除（最大節約）
# Railway Dashboard > Settings > Environments > staging > Delete

# STG環境再作成（必要時）
railway environment new staging
# Dashboard > Duplicate from production
railway run python manage.py loaddata airs/fixtures/*.json
```

# 実用的運用スケジュール
- **開発期間**: STG環境フル稼働
- **開発休止期間（1-2週間）**: App Sleep任せ（自動）
- **長期休止期間（1ヶ月以上）**: 環境削除を検討
```

### 旧Herokuデプロイ関連（非推奨）
```bash
# Herokuにデプロイ
git push heroku main

# Herokuでマイグレーション実行
heroku run python manage.py migrate

# Herokuログ確認
heroku logs --tail

# Heroku環境でbashセッション開始
heroku run --app=[環境名] bash

# Heroku環境でのライブラリ確認
heroku run --app=[環境名] pip list
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
- django-herokuでHeroku環境に最適化

### Heroku環境構成
- **rnsite-stg**: Eco Dynos + Heroku Postgres Mini + Papertrail Choklad
- **rnsite-prod**: Basic Dynos + Heroku Postgres Basic + Papertrail Choklad

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

### 使用ライブラリ（独自選択分）
- `pytz`: タイムゾーン変換
- `beautifulsoup4`: WEBスクレイピング & HTMLパーサ
- `mojimoji`: 全角半角変換
- `urlextract`: 文字列からURL抽出

## Railway移行について

### Railway移行の利点
- **コスト削減**: Herokuより安価な料金体系
- **簡単なデプロイ**: GitHubリポジトリからの自動デプロイ
- **モダンな開発体験**: より直感的なUI/UX

### 移行手順
1. **Railway設定**: GitHubリポジトリを接続
2. **環境変数設定**: `SECRET_KEY`, `DATABASE_URL`等を設定
3. **PostgreSQLサービス**: Railwayで新しくPostgreSQLを作成
4. **データ移行**: Herokuからデータをエクスポート/インポート

### 必要な環境変数
```
SECRET_KEY=django_secret_key
DATABASE_URL=postgresql://user:password@host:port/dbname
SENTRY_DSN=sentry_dsn_url（任意）
```

### コード変更点
- `django-heroku` → `dj-database-url` + WhiteNoise設定
- `ALLOWED_HOSTS = ['*']` でRailwayドメインに対応
- `railway.json`でデプロイ設定を自動化
- `psycopg2-binary`でPostgreSQL接続を確保