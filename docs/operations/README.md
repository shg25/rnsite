# 運用・保守ドキュメント

このディレクトリには、本番環境の運用・保守に関するドキュメントが含まれています。

## 📋 ドキュメント一覧（今後追加予定）

### バックアップ・復旧
- **backup-system.md** - 自動バックアップシステムの詳細
- **disaster-recovery.md** - 障害復旧手順

### 監視・アラート
- **monitoring.md** - 監視設定・ヘルスチェック
- **alerting.md** - アラート設定・通知設定

### 保守・メンテナンス
- **maintenance.md** - 定期メンテナンス手順
- **troubleshooting.md** - 一般的なトラブルシューティング

## 🔧 現在の運用システム

### 自動バックアップシステム（稼働中）

[backup-service/](../../backup-service/) ディレクトリで完全自動バックアップが稼働中：

```bash
# 基本仕様
- 週1回自動実行（日曜14時JST）
- AWS S3クラウド保存
- サイズ異常検知・Slack通知
- 前回データ自動削除
- コスト: 約$0.04/月（5円程度）
```

### ヘルスチェック機能
```bash
# エンドポイント
GET /health/

# 機能
- データベース接続確認
- サービス稼働状況確認
- JSON形式での応答
```

### Railway運用
```bash
# 基本的な運用コマンド
railway logs              # ログ確認
railway status            # サービス状況確認
railway variables         # 環境変数確認

# 緊急時対応
railway restart           # サービス再起動
railway rollback          # 前バージョンに戻す
```

## 📊 監視・アラート

### Railway標準監視
- アプリケーション稼働状況
- リソース使用量（CPU/Memory/Network）
- デプロイ状況

### カスタム監視（実装済み）
- データベース接続状況（ヘルスチェック）
- バックアップ成功/失敗（Slack通知）
- データサイズ異常検知（容量変化監視）

## 💰 コスト管理

### 月次コスト監視
```bash
# Railway Dashboard > Usage
- 現在の使用量確認
- 月間コスト予測
- サービス別使用量分析
```

### コスト最適化施策
- App Sleep活用（STG環境）
- 不要サービスの定期削除
- Railway Metalの自動適用（2025年Q1予定）

## 🔗 関連リソース

### バックアップシステム
- [backup-service/](../../backup-service/) - 自動バックアップサービス本体
- [backup-service/README.md](../../backup-service/README.md) - 詳細ドキュメント

### 設定ファイル
- [CLAUDE.md](../../CLAUDE.md) - 運用コマンド・手順の詳細
- [railway.json](../../railway.json) - Railway デプロイ設定

## 🚧 TODO

このディレクトリは今後以下のドキュメントで充実させる予定です：

- [ ] バックアップ・復旧詳細手順
- [ ] 監視・アラート設定ガイド
- [ ] パフォーマンス分析手順
- [ ] セキュリティ監査ガイドライン
- [ ] インシデント対応手順書