# STG環境手動作成手順書

## 概要
HerokuからRailway移行に伴うSTG環境の手動セットアップ手順。本番環境と分離したテスト環境を構築し、安全な開発・デプロイフローを実現します。

## 前提条件
- Railway CLI がインストール済み (`npm install -g @railway/cli`)
- Railway アカウントでログイン済み (`railway login`)
- 本番環境が既に稼働中

## STG環境運用のベストプラクティス

### コスト最適化のポイント
```bash
# 🔥 重要: 月初作成で最大活用
10/1作成 → 丸々1ヶ月間活用可能（最もお得）
9/30作成 → 1日分料金で10月分も満額課金（損失大）

# 💡 効率的な運用サイクル
作成 → テスト・開発 → 不要時は即座に削除 → 必要時に再作成（5分）
```

### 4つの基本方針
1. **月初作成**: 月の初め（1-3日）に作成して最大活用
2. **即座削除**: 使わない期間は迷わず削除（日割り課金停止）
3. **App Sleep活用**: 自動コスト削減（設定不要・10分で自動スリープ）
4. **柔軟な再作成**: 必要時に素早く再構築（約5分で完了）

### 実践的な開発スケジュール例
```bash
# 月初パターン（推奨）
10/1: STG環境作成 + 開発開始
10/15: 開発完了 → 本番デプロイ → STG環境削除
10/20: 新機能開発 → STG環境再作成
10/31: 月末処理 → STG環境削除

# 短期テストパターン
随時: STG環境作成 → テスト（数日間）→ 即座削除
コスト: 実際の使用日数分のみ（例: 7日間 = $1-2程度）
```

## STG環境の標準パターン

### 基本方針: 完全分離型 + App Sleep活用
- **安全性**: 本番環境から完全分離、誤操作リスクゼロ
- **コスト効率**: App Sleep自動適用で$1-3/月に削減
- **運用シンプル**: 迷わず実行できる標準手順

**用途**: すべてのSTG環境ニーズに対応
- DB変更を伴う開発・Migration テスト  
- フロントエンド修正・UI テスト
- 新機能の安全な検証
- 緊急時の動作確認

### STG環境の作成手順

#### STEP 1: STG環境の作成
```bash
# 1. 現在のプロジェクトを確認
railway status

# 2. staging環境を新規作成
railway environment new staging

# 3. staging環境に切り替え
railway environment staging

# 4. Railway Dashboard で本番環境設定をコピー
# ブラウザで Railway Dashboard > Settings > Environments > staging > "Duplicate from production"
```

#### STEP 2: PostgreSQL サービス追加
```bash
# STG環境にPostgreSQLを追加
railway add postgresql

# 環境変数の確認（DATABASE_URLが自動設定される）
railway variables

# 出力例:
# DATABASE_URL=postgresql://postgres:password@monorail.proxy.rlwy.net:12345/railway
```

#### STEP 3: STG専用環境変数設定
```bash
# 必須環境変数の設定
railway variables set SECRET_KEY="stg-specific-secret-key-here"
railway variables set DEBUG="False"

# STG環境識別用
railway variables set RAILWAY_ENVIRONMENT="staging"

# 任意: Sentry設定（STG専用DSN推奨）
railway variables set SENTRY_DSN="https://your-stg-sentry-dsn@sentry.io/project"

# カスタムドメイン（任意）
railway variables set CUSTOM_DOMAIN="stg.your-domain.com"
```

#### STEP 4: データベース初期化
```bash
# マイグレーション実行
railway run python manage.py migrate

# テストデータ投入（374オブジェクト）
railway run python manage.py loaddata airs/fixtures/broadcasters.json
railway run python manage.py loaddata airs/fixtures/programs.json  
railway run python manage.py loaddata airs/fixtures/airs.json
railway run python manage.py loaddata airs/fixtures/users.json
railway run python manage.py loaddata airs/fixtures/nanitoris.json

# または一括投入
railway run python manage.py loaddata airs/fixtures/*.json

# 管理者ユーザー作成（任意）
railway run python manage.py createsuperuser
```

#### STEP 5: デプロイとテスト
```bash
# developブランチをSTG環境にデプロイ
git checkout develop  # 開発ブランチに切り替え
git push origin develop

# Railway Dashboard で Manual Deploy または GitHub連携設定
# Settings > Source > Connect Repository > Branch: develop

# デプロイ確認
railway logs
railway status

# ヘルスチェック確認
curl https://your-stg-app.railway.app/health/
```

### App Sleep によるコスト最適化（自動適用）

STG環境では**App Sleep が自動的に有効**になり、大幅なコスト削減が実現されます：

```bash
# App Sleep の動作（設定不要・自動）
10分非アクティブ → 自動スリープ → CPU/Memory課金停止
アクセス時 → 自動復帰（数秒～10秒程度）

# コスト削減効果
通常稼働: $7-10/月（24時間稼働）
Sleep活用: $1-3/月（実働時間のみ課金）

# 注意事項
- 初回アクセス時に「Application failed to respond」が表示される場合あり
- すぐにリフレッシュすれば正常に復帰
- 本番環境では無効化推奨（ユーザー体験悪化防止）
```

## デプロイフロー

### 開発 → STG → 本番フロー
```bash
# 1. 開発ブランチで作業
git checkout develop
# 開発作業...
git add .
git commit -m "新機能: XXXを追加"
git push origin develop

# 2. STG環境でテスト
railway environment staging
railway logs  # デプロイ確認
# ブラウザでSTG環境での動作確認

# 3. STG環境でOKなら本番にマージ
git checkout main
git merge develop
git push origin main

# 4. 本番環境デプロイ確認
railway environment production  
railway logs
```

### 緊急時の直接本番デプロイ
```bash
# STGスキップして緊急デプロイ
git checkout main
# 緊急修正...
git add .
git commit -m "hotfix: 緊急修正"
git push origin main

# 事後にdevelopブランチにも反映
git checkout develop
git merge main
git push origin develop
```

## STG環境での動作確認チェックリスト

### 基本動作確認
- [ ] アプリケーション起動確認
- [ ] ヘルスチェック (`/health/`) 正常応答
- [ ] 管理画面アクセス確認
- [ ] ユーザー認証・ログイン確認

### データ確認
- [ ] 放送一覧表示確認
- [ ] 何卒（聴取記録）作成・表示確認  
- [ ] データベース接続確認
- [ ] 検索機能動作確認

### 新機能テスト
- [ ] Migration実行確認
- [ ] 新機能の動作確認
- [ ] エラーログ確認 (`railway logs`)
- [ ] パフォーマンス確認

## トラブルシューティング

### よくある問題と解決方法

#### DATABASE_URLが設定されていない
```bash
railway variables
# DATABASE_URLが無い場合
railway add postgresql  # PostgreSQL追加
railway variables       # 再確認
```

#### マイグレーションエラー
```bash
# マイグレーション状態確認
railway run python manage.py showmigrations

# 特定マイグレーションの強制適用
railway run python manage.py migrate --fake-initial

# マイグレーションリセット（危険・STGのみ）
railway run python manage.py migrate airs zero
railway run python manage.py migrate
```

#### 静的ファイルが表示されない
```bash
# 静的ファイル収集実行
railway run python manage.py collectstatic --noinput -v 2

# WhiteNoise設定確認
railway run python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATICFILES_STORAGE)
>>> exit()
```

#### App Sleep による初回アクセスエラー
```bash
# 症状: "Application failed to respond"
# 解決: ページをリフレッシュ（10秒程度で復帰）

# スリープを防ぐ方法（開発時のみ）
# 定期的なアクセスで維持（本番環境では非推奨）
```

## Railway課金体系（詳細）

### 基本的な課金方式
**従量制課金（Pay-as-you-go）** - 使った分だけ課金

#### 課金タイミング
```bash
# ❌ 課金開始ではないタイミング
railway environment new staging     # 環境作成のみでは課金なし
railway service create web          # サービス作成のみでは課金なし

# ✅ 課金開始タイミング  
railway up                          # アプリデプロイ時から課金開始
railway add postgresql              # PostgreSQL追加と同時に課金開始
```

#### 課金期間
**暦月ベース（1日〜末日）** - 日割り計算あり

```bash
# 例: 9/13にSTG環境作成した場合
作成日: 2025/9/13
9月課金: 2025/9/13 〜 2025/9/30 (18日分の日割り)
10月課金: 2025/10/1 〜 2025/10/31 (31日分の満額)

# 削除時は即座に課金停止
railway environment delete staging  # 削除日まで日割り課金
```

#### 実際の課金例
```bash
# パターンA: 月初作成（最もお得）
10/1作成 → 丸々1ヶ月活用可能

# パターンB: 月末作成（割高）
9/30作成 → 1日分料金で10月まで継続課金

# パターンC: 短期利用
9/13作成 → 9/20削除 = 7日分のみ課金
PostgreSQL: $7/月 × (7日/30日) = $1.63
Web Service: $5/月 × (7日/30日) = $1.17
```

### App Sleep による自動コスト削減
```bash
# STG環境での実際のコスト削減効果
通常稼働: $5/月（24時間稼働）
Sleep活用: $1-2/月（10分非アクティブで自動スリープ）

# スリープ時の課金
CPU/Memory: 停止 → 課金なし ✅
Storage: 継続 → 継続課金
Network: 停止 → 課金なし ✅
```

### Railway Metal の影響（2025年Q1予定）
```bash
# 現在の料金レート
Storage: $0.25/GB/月
Network: $0.10/GB/月

# Railway Metal適用後（40-50%削減）
Storage: $0.15/GB/月  
Network: $0.05/GB/月

# 既存ユーザーは自動適用予定（追加設定不要）
```

## コスト管理

### STG環境の実際のコスト（App Sleep適用後）
- **通常時**: $1-3/月（自動スリープによる大幅削減）
- **削除時**: $0/月（環境削除で即座に課金停止）
- **短期利用**: 日割り計算（例: 7日間利用 = $1-2程度）

### コスト削減のベストプラクティス
```bash
# 1. 使用しない期間は環境削除
railway environment delete staging  # 完全削除

# 2. App Sleep を活用（自動・推奨）
# 設定不要・10分で自動スリープ

# 3. 定期的なコスト確認
# Railway Dashboard > Usage で月次コスト監視
```

## まとめ

### STG環境の標準運用
**1つのシンプルな方針**: 完全分離型 + App Sleep活用

**運用のポイント**:
1. **月初作成**で最大活用（月末作成は損失大）
2. **develop → staging → main** の安全な開発フロー遵守
3. **STG環境での十分なテスト**実施
4. **不要時は即座に削除**でコスト削減（再作成5分）
5. **App Sleep自動適用**で$1-3/月の低コスト運用

### 運用サイクル
```bash
月初: STG環境作成 + 開発開始
開発: テスト・修正・検証
完了: 本番デプロイ + STG環境削除
必要時: 素早く再作成（5分）
```

**結果**: 安全 + 低コスト + シンプル運用の実現

この標準手順で、迷わず効率的なSTG環境を構築・運用してください。