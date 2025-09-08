# PostgreSQL スマートバックアップサービス

PostgreSQL データベースの自動バックアップ、異常検知、Slack通知を行うスマートバックアップシステム

## アーキテクチャ図

```
┌─────────────────────────── Railway Platform ───────────────────────────┐
│                                                                          │
│  ┌─────────────────────────┐    Network     ┌─────────────────────────┐  │
│  │     backup-service      │◄──────────────►│   PostgreSQL Service    │  │
│  │    (Docker Container)   │   Connection    │    (Docker Container)   │  │
│  │                         │                 │                         │  │
│  │  ┌─────────────────────┐│                 │ ┌─────────────────────┐ │  │
│  │  │     Node.js App     ││                 │ │   PostgreSQL v17.6  │ │  │
│  │  │  ┌─────────────────┐││                 │ │                     │ │  │
│  │  │  │ cron-backup.js  │││                 │ │   Database Tables   │ │  │
│  │  │  │ (Scheduler)     │││                 │ │   - Air             │ │  │
│  │  │  └─────────────────┘││                 │ │   - Broadcaster     │ │  │
│  │  │  ┌─────────────────┐││   pg_dump       │ │   - Program         │ │  │
│  │  │  │smart-backup.js  │││◄────────────────┤ │   - Nanitozo        │ │  │
│  │  │  │ (Main Logic)    │││   DATABASE_URL  │ │   - etc...          │ │  │
│  │  │  └─────────────────┘││                 │ └─────────────────────┘ │  │
│  │  │  ┌─────────────────┐││                 └─────────────────────────┘  │
│  │  │  │ pg_dump v17     │││                                              │
│  │  │  │ (PostgreSQL     │││                                              │
│  │  │  │  Client)        │││                                              │
│  │  │  └─────────────────┘││                                              │
│  │  └─────────────────────┘│                                              │
│  └─────────────────────────┘                                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
                │                               │
                │ HTTPS Upload                  │ HTTPS POST
                ▼                               ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│      AWS S3 Bucket      │         │      Slack Webhook      │
│    (External Service)   │         │    (External Service)   │
│                         │         │                         │
│ ┌─────────────────────┐ │         │ ┌─────────────────────┐ │
│ │ Encrypted Backups   │ │         │ │   Notification      │ │
│ │ - weekly-backup-    │ │         │ │   Messages:         │ │
│ │   2025-09-04T       │ │         │ │   ✅ Success        │ │
│ │   02-30-00.sql      │ │         │ │   ⚠️ Anomaly        │ │
│ │ - Previous backups  │ │         │ │   ❌ Error          │ │
│ │ - Size metadata     │ │         │ └─────────────────────┘ │
│ └─────────────────────┘ │         └─────────────────────────┘
└─────────────────────────┘
```

## 機能概要

### 🎯 主要機能
- **自動バックアップ**: PostgreSQL データベースの定期バックアップ
- **サイズ異常検知**: 前回比50%以上の変化を検出
- **スマート保持機能**: 異常検知時は前回バックアップを安全保持
- **3パターン通知**: 成功/異常/失敗の状況別Slack通知
- **暗号化ストレージ**: AWS S3での暗号化保存

### 📊 処理フロー
```
1. cron-backup.js (Scheduler)
   │ 毎週月曜 4:00 JST トリガー
   ▼
2. smart-backup.js (Main Logic)
   │ ┌─ 前回バックアップ情報取得 (S3)
   │ ├─ pg_dump実行 (PostgreSQL Service)
   │ ├─ サイズ異常検知
   │ ├─ S3暗号化アップロード
   │ ├─ 前回ファイル削除判定
   │ └─ Slack通知送信
   ▼
3. 外部サービス連携
   ├─ AWS S3: バックアップファイル保存
   └─ Slack: 結果通知
```

## ファイル構成

```
backup-service/
├── README.md              # このファイル
├── package.json           # Node.js依存関係
├── package-lock.json      # 依存関係ロック
├── jest.config.js         # Jestテスト設定
├── Dockerfile            # Dockerコンテナ設定
├── cron-backup.js        # cronスケジューラー
├── smart-backup.js       # メインバックアップロジック
└── __tests__/            # テストファイル
    ├── smart-backup.test.js
    └── cron-backup.test.js
```

### 各ファイルの役割

| ファイル | 役割 | 説明 |
|---------|------|------|
| `smart-backup.js` | メインロジック | バックアップ処理、異常検知、通知機能 |
| `cron-backup.js` | スケジューラー | 定期実行制御、graceful shutdown |
| `Dockerfile` | コンテナ設定 | PostgreSQL v17対応クライアント構築 |
| `package.json` | 依存関係管理 | jest, aws-sdk, node-cron, pg |
| `jest.config.js` | テスト設定 | Jestテスト環境とカバレッジ設定 |
| `__tests__/` | テストディレクトリ | ユニットテストとスケジューラーテスト |

## 環境変数設定

### 必須環境変数
```bash
# データベース接続
DATABASE_URL=postgresql://user:pass@host:port/database

# AWS S3設定
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_S3_REGION=ap-northeast-1  # オプション（デフォルト: ap-northeast-1）

# Slack通知
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# バックアップ設定
BACKUP_CRON_SCHEDULE=0 19 * * 1  # 毎週月曜 4:00 JST (UTC 19:00 日曜)
BACKUP_SIZE_THRESHOLD=50         # サイズ異常検知閾値（%）
BACKUP_PREFIX=weekly-backup      # ファイル名プレフィックス
```

## Slack通知パターン

### 1. ✅ 正常バックアップ
```
✅ Weekly backup completed successfully: 1.73MB (2.5% change from previous backup). Previous backup deleted.
```

### 2. ⚠️ サイズ異常検知
```
⚠️ Weekly backup completed with size anomaly: 5.82MB (75.2% change from previous backup). Previous backup preserved for safety.
```

### 3. ❌ バックアップ失敗
```
❌ Weekly backup failed: Connection timeout. Please check the system immediately.
```

## PostgreSQL v17対応

### バージョン互換性対応
このシステムはRailwayのPostgreSQL v17.6サーバーに最適化されています。

#### Dockerfileの段階的インストール戦略
```dockerfile
# PostgreSQL v17サーバー対応：v17専用クライアント→最新安定版→v16の順でフォールバック
RUN apk update && \
    (apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main postgresql17-client || \
     apk add --no-cache postgresql-client || \
     apk add --no-cache postgresql16-client)
```

#### 複数コマンドフォールバック
```javascript
const dumpCommands = [
  `pg_dump "${DATABASE_URL}" --no-password --compress=0 --verbose > ${filename}`, // 最新機能版（v17対応）
  `pg_dump "${DATABASE_URL}" --compress=0 > ${filename}`,                         // 基本版（圧縮無効）
  `pg_dump "${DATABASE_URL}" > ${filename}`                                       // 最小限版（最高互換性）
];
```

## 運用・監視

### 🔍 ログ確認
```bash
# Railway CLI使用
railway logs -s backup-service

# 主要ログメッセージ
✅ Dump completed: 1.73MB
📱 Slack notification sent successfully  
🗑️ Deleted previous backup: weekly-backup-xxx.sql
```

### 📈 監視ポイント
- **バックアップサイズの推移**: 急激な増減がないか
- **Slack通知の受信**: 毎週月曜朝の通知確認
- **S3ストレージ使用量**: 適切なファイル削除ができているか

### 🚨 トラブルシューティング

#### よくある問題と対処法

| 問題 | 原因 | 対処法 |
|------|------|--------|
| pg_dumpが失敗 | PostgreSQLバージョン不一致 | Dockerfileのフォールバック機能で自動対応 |
| Slack通知が届かない | WEBHOOK_URL設定ミス | Railway環境変数を再確認 |
| S3アップロード失敗 | AWS認証エラー | ACCESS_KEY, SECRET_KEYを再設定 |
| ファイルサイズ異常 | データベース構造変更 | 正常な変更であれば次回実行で解消 |

## テスト

### 🧪 テスト実行手順

#### 初回セットアップ
```bash
# 1. backup-serviceディレクトリに移動
cd backup-service

# 2. 依存関係インストール（初回のみ）
npm install
```

#### テスト実行
```bash
# 全テスト実行
npm test

# ウォッチモードでテスト実行（ファイル変更時に自動再実行）
npm run test:watch

# カバレッジ付きテスト実行
npm run test:coverage
```

#### 期待される出力例
```
PASS __tests__/smart-backup.test.js
PASS __tests__/cron-backup.test.js

Test Suites: 2 passed, 2 total
Tests:       21 passed, 21 total
Snapshots:   0 total
Time:        1.6 s
```

> **注意**: このテストはDjango側のテスト（`python manage.py test`）とは完全に独立しています。Node.js環境で実行されます。

### 📊 テスト構成
```
__tests__/
├── smart-backup.test.js    # メインロジックのユニットテスト
└── cron-backup.test.js     # cronスケジューラーのテスト
```

### 🎯 テスト対象
| 機能 | テスト内容 | 重要度 |
|------|------------|--------|
| `checkSizeChange` | サイズ異常検知ロジック | 🔴 高 |
| `sendSlackNotification` | Slack通知の基本処理 | 🟡 中 |
| `cleanupLocalFile` | ローカルファイル削除 | 🟢 低 |
| 環境変数処理 | 設定値の読み込み確認 | 🟡 中 |
| cronスケジュール | 定期実行設定の確認 | 🟡 中 |

### 📈 カバレッジ目標
- **Branches**: 60%以上
- **Functions**: 70%以上  
- **Lines**: 70%以上
- **Statements**: 70%以上

## デプロイ・更新手順

### 初回デプロイ
1. Railway プロジェクト作成
2. 環境変数設定
3. Dockerコンテナのデプロイ

### 更新時
```bash
# コード更新後（自動テストが実行されます）
git add backup-service/
git commit -m "バックアップシステム更新"  # ← pre-commitフックでテスト自動実行
git push origin railway-migration

# Railway自動デプロイまたは手動デプロイ
railway redeploy -s backup-service --yes
```

> **自動テスト実行**: backup-service配下のファイル変更時、Git pre-commitフックで自動的にテストが実行されます。テスト失敗時はコミットが中止されます。

## セキュリティ

- ✅ **AWS S3**: AES256サーバーサイド暗号化
- ✅ **環境変数**: 機密情報の安全な管理
- ✅ **ネットワーク**: HTTPS通信のみ
- ✅ **アクセス制御**: S3バケットの適切な権限設定

## ライセンス

MIT License

---

📝 **最終更新**: 2025年9月8日  
🏗️ **対応環境**: Railway Platform, PostgreSQL v17.6, Node.js 18+  
🧪 **テスト**: Jest 29.7.0, 21テスト, 自動実行対応