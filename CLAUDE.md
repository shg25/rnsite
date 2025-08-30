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

## 週1回自動バックアップシステム（高機能版）

### セットアップ手順
```bash
# 1. Railway S3 Backup Template をデプロイ
# https://railway.app/template/XV2dlg にアクセス
# "Deploy Now" をクリック

# 2. 環境変数設定
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key  
AWS_S3_BUCKET=your-backup-bucket-name
AWS_S3_REGION=ap-northeast-1
BACKUP_DATABASE_URL=$DATABASE_URL
BACKUP_CRON_SCHEDULE="0 5 * * 0"  # 毎週日曜日 5:00 AM UTC (日本時間14:00)

# 3. 高機能版の追加設定（容量チェック + 前回データ削除）
BACKUP_SIZE_CHECK_ENABLED=true
BACKUP_SIZE_THRESHOLD=50  # 50%の増減でアラート
BACKUP_RETENTION_WEEKS=1  # 1週間分のみ保持
SLACK_WEBHOOK_URL=your_slack_webhook_url  # 異常通知用（任意）
```

### 高機能バックアップの仕様
```javascript
// バックアップ処理のフロー
1. 現在のDBをdump
2. ファイルサイズをチェック
3. 前回バックアップとサイズ比較
4. 異常がなければS3にアップロード
5. 前回のバックアップファイルを削除
6. ログ記録 & 通知（必要に応じて）

// 容量チェックロジック
const currentSize = backupFile.size;
const previousSize = await getPreviousBackupSize();
const changePercent = Math.abs((currentSize - previousSize) / previousSize * 100);

if (changePercent > BACKUP_SIZE_THRESHOLD) {
  // アラート送信（Slack等）
  await sendAlert(`DB size changed by ${changePercent}%`);
}
```

### 想定される動作
```bash
# 正常時（毎週日曜日14:00 JST）
2025-09-07 14:00: バックアップ開始
2025-09-07 14:01: DB dump完了 (97.5MB)
2025-09-07 14:01: サイズチェックOK (前回比+0.2%)  
2025-09-07 14:01: S3アップロード完了
2025-09-07 14:01: 前回ファイル削除
2025-09-07 14:01: バックアップ完了

# 異常検知時
2025-09-14 14:00: バックアップ開始
2025-09-14 14:01: DB dump完了 (150MB)
2025-09-14 14:01: ⚠️ サイズ異常検知 (前回比+54%)
2025-09-14 14:01: Slack通知送信
2025-09-14 14:01: バックアップは継続実行
2025-09-14 14:01: 前回ファイル削除
```

### コスト試算
```bash
# 週1回バックアップ（97.3MB）
- S3ストレージ: 1つのファイルのみ保持 = $0.002/月
- Railway→S3転送: 0.097GB × 4回/月 × $0.10 = $0.039/月
- バックアップサービス: Railway App Sleep で自動節約
- 合計: 約$0.04/月（5円程度）

# Railway Metal適用後（2025年Q1以降）
- 転送コスト50%削減: $0.019/月
- 合計: 約$0.02/月（3円程度）
```

## Railway料金体系（2025年最新版）

### 基本料金構造
```bash
# Hobby Plan: $5/月（$5使用量クレジット付き）
# 使用量が$5以下なら追加料金なし
# $5超過分のみ追加課金

# 現在の使用量ベース課金レート
- CPU: $20/vCPU/月
- Memory: $10/GB/月  
- Volume(ストレージ): $0.25/GB/月（現行）→ $0.15/GB/月（Railway Metal）
- Network Egress(データ転送): $0.10/GB/月（現行）→ $0.05/GB/月（Railway Metal）

# Railway Metal（2025年Q1完了予定）
# 80%のワークロードがRailway Metal移行で自動適用
# ストレージ40%削減、転送料50%削減
```

### PostgreSQLのコスト構成
```bash
# データベースの実際のコスト要因
1. CPU使用量: クエリ処理時のみ課金
2. Memory使用量: データキャッシュ等
3. Volume使用量: DB データサイズ（現在97.3MB）
4. Network Egress: 外部へのデータ転送

# 97.3MBデータベースの月間コスト例
# 現行レート
- Volume: 0.097GB × $0.25 = $0.024/月
- CPU/Memory: 低負荷時は数十円程度/月
- 合計: $1-2程度/月（$5クレジット内）

# Railway Metal適用後（2025年Q1以降）
- Volume: 0.097GB × $0.15 = $0.015/月（40%削減）
```

### バックアップのコスト影響
```bash
# 週1回バックアップ（97.3MB）の追加コスト
- S3 Standard Storage: 0.097GB × $0.023 = $0.002/月
- Network Egress（Railway→S3）: 
  現行: 0.097GB × 4回/月 × $0.10 = $0.039/月
  Railway Metal: 0.097GB × 4回/月 × $0.05 = $0.019/月（50%削減）
- 合計追加コスト: 約$0.04/月 → $0.02/月（Railway Metal適用後）

# 前回データ削除による節約効果
- ストレージを1週間分のみ保持 → 実質コスト変化なし
- 長期蓄積なしで最小限のS3料金
- スマートな容量チェックで異常検知も可能
```
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
- **STG**: テストデータ（fixturesファイル使用）または本番データ（リアルデータテスト用）
- **本番**: 実データ（本番運用データ）

## STGデータの選択肢

### パターンA: テストデータ使用
```bash
railway environment staging
railway run python manage.py loaddata airs/fixtures/*.json  # 374オブジェクトのテストデータ
```

### パターンB: 本番データ使用（リアルデータテスト）
```bash
# 1. 本番データをバックアップ
railway environment production
railway run pg_dump $DATABASE_URL -Ft > production_backup_$(date +%Y%m%d).dump

# 2. STG環境に本番データを投入
railway environment staging
# 注意: STGの既存データは削除される
railway run pg_restore -d $DATABASE_URL --clean --no-owner production_backup_$(date +%Y%m%d).dump

# 3. マイグレーション実行（必要に応じて）
railway run python manage.py migrate
```

### パターンC: 本番データの匿名化版
```bash
# 本番データを匿名化してSTGに投入
railway environment production
railway run pg_dump $DATABASE_URL --data-only -Ft > production_data.dump

railway environment staging
# カスタムスクリプトで個人情報をマスク
railway run python manage.py anonymize_data  # 独自実装が必要
railway run pg_restore -d $DATABASE_URL --data-only production_data.dump
```

## 本番データ投入時の考慮事項

### コスト影響（軽微）
- **現在サイズ**: 本番97.3MB → STGにも97.3MB
- **追加コスト**: 数十円程度/月（PostgreSQLストレージ料金）
- **転送コスト**: 1回限り数円程度

### リスク管理
```bash
# 1. データ投入前のSTGバックアップ
railway environment staging  
railway run pg_dump $DATABASE_URL -Ft > stg_before_$(date +%Y%m%d).dump

# 2. 本番データ投入
pg_restore -d $STG_DATABASE_URL --clean production_backup.dump

# 3. 問題があった場合の復旧
pg_restore -d $STG_DATABASE_URL --clean stg_before_$(date +%Y%m%d).dump
```

### セキュリティ考慮
- 本番ユーザーデータの適切な取り扱い
- 必要に応じて個人情報の匿名化
- STG環境へのアクセス制限確認

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

# STG環境の4つの運用パターン

## パターン1: 完全分離型（標準）
- **Web**: STG専用
- **DB**: STG専用（テストデータ）
- **用途**: DB変更を伴う開発、Migration テスト
- **コスト**: Web + DB
```bash
railway environment staging
# Dashboard > Duplicate from production
railway run python manage.py loaddata airs/fixtures/*.json
```

## パターン2: 本番DB共有型（効率重視） ⭐
- **Web**: STG専用  
- **DB**: 本番DB共有（READ-ONLY）
- **用途**: フロントエンド修正、表示確認、UI テスト
- **コスト**: Web のみ（DB料金節約）
```bash
railway environment staging
# Dashboard > web service のみ作成
railway variables set DATABASE_URL=$PRODUCTION_DATABASE_URL
# 注意：READ-ONLY運用必須
```

## パターン3: App Sleep 活用型（STG専用推奨）
- **運用**: 10分非アクティブで自動スリープ、アクセス時に自動復帰
- **コスト**: 最小限（自動制御）
- **注意**: 本番環境では非推奨（ユーザー体験悪化のため）

### App Sleep の詳細仕様
```bash
# スリープ条件
- 10分間アウトバウンドトラフィック無し
- DB接続、テレメトリ、外部API呼び出し等が対象

# 復帰条件  
- インターネットからのリクエスト
- 初回リクエストでウェイクアップ（コールドブート時間あり）

# 本番環境での問題
- 初回アクセス時に "Application failed to respond" エラー
- 即座にリフレッシュ必要でユーザー体験悪化
- 環境別設定不可（プロジェクト全体に適用）

# スリープを防ぐ要因
- アクティブなDB接続プール
- フレームワークのテレメトリ（Next.js等）  
- 定期的な外部API呼び出し
```

## パターン4: 完全削除型  
- **運用**: 使わない期間は完全削除
- **コスト**: ゼロ（再作成5分）

# 実用的運用スケジュール
- **DB影響なし修正**: パターン2（本番DB共有）推奨
- **DB変更あり修正**: パターン1（完全分離）
- **開発休止期間（1-2週間）**: App Sleep任せ（自動）
- **長期休止期間（1ヶ月以上）**: 環境削除を検討

# 本番DB共有時の安全対策
```sql
-- 本番DB内でSTG専用読み取り専用ユーザー作成
CREATE USER staging_readonly WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO staging_readonly;
GRANT USAGE ON SCHEMA public TO staging_readonly;
```

```python
# settings.py でSTG環境のWrite操作制限
if os.getenv('RAILWAY_ENVIRONMENT') == 'staging':
    # Read-Only 接続推奨
    pass
```
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

### Railway本番環境の料金詳細（2025年最新）
- **基本プラン**: $5/月（従量制超過分も含む）
- **PostgreSQL**: 計算量とストレージ使用量に基づく従量制
- **実際のコスト**: PostgreSQL約$7-8/月（高使用量のため）+ Web $5/月 = 約$12-13/月
- **比較**: Heroku $16/月 → Railway $12-13/月 で約25%削減

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

### Railway導入手順
```bash
# 1. Railwayで新しいサービス作成
railway service create backup-service

# 2. backup-serviceディレクトリに移動
cd backup-service

# 3. 環境変数設定
railway variables set DATABASE_URL=$RAILWAY_MAIN_DATABASE_URL
railway variables set AWS_ACCESS_KEY_ID=your_aws_key
railway variables set AWS_SECRET_ACCESS_KEY=your_aws_secret
railway variables set AWS_S3_BUCKET=your_backup_bucket_name
railway variables set SLACK_WEBHOOK_URL=your_slack_webhook_url

# 4. cronサービスとしてデプロイ
railway up
```

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

### AWS S3設定手順
```bash
# 1. S3バケット作成
aws s3 mb s3://your-backup-bucket --region ap-northeast-1

# 2. IAMユーザー作成とポリシー添付
aws iam create-user --user-name railway-backup-user

# 3. 必要な権限（S3フルアクセス）
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow", 
            "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
            "Resource": ["arn:aws:s3:::your-backup-bucket/*", "arn:aws:s3:::your-backup-bucket"]
        }
    ]
}
```

### バックアップ運用フロー
1. **スケジュール起動**: 毎週日曜5AM UTC（日本時間14時）
2. **前回サイズ取得**: S3から最新バックアップサイズ確認
3. **データベースダンプ**: `pg_dump`で完全バックアップ作成
4. **サイズ異常検知**: 50%以上の変化でSlackアラート送信
5. **S3アップロード**: AES256暗号化でクラウド保存
6. **前回ファイル削除**: 古いバックアップを自動削除
7. **ローカルクリーンアップ**: 一時ファイル削除
8. **実行結果通知**: 成功/失敗をSlack通知

### ログ出力例
```
🚀 Starting smart backup process...
📅 2025/08/31 14:00:00
📊 Previous backup: 2.45MB
📦 Creating database dump: weekly-backup-2025-08-31.sql
✅ Dump completed: 2.52MB
📈 Size change: 2.9% (threshold: 50%)
☁️ Uploading to S3: weekly-backup-2025-08-31.sql
✅ Upload completed
🗑️ Deleted previous backup: weekly-backup-2025-08-24.sql
🧹 Cleaned up local file: weekly-backup-2025-08-31.sql
🎉 Smart backup completed successfully!
✅ Weekly backup: 2.52MB (2.9% change)
```

### 手動実行方法
```bash
# バックアップサービス内で単発実行
railway run node smart-backup.js

# または、Railway環境で直接実行
railway exec node smart-backup.js
```