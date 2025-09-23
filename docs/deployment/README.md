# デプロイ・環境構築ドキュメント

このディレクトリには、環境構築・デプロイに関するドキュメントが含まれています。

## 📋 ドキュメント一覧

### STG環境関連
- **[stg-environment-setup.md](./stg-environment-setup.md)** - STG環境の手動作成手順書
  - Railway STG環境の標準セットアップ手順
  - App Sleep活用によるコスト最適化
  - 月初作成・不要時削除の運用指針

### Railway移行関連
- **[railway-deployment-checklist.md](./railway-deployment-checklist.md)** - Railway移行チェックリスト
  - HerokuからRailwayへの移行手順
  - 移行前後の確認項目
  - トラブルシューティング

## 🚀 クイックスタート

### STG環境を今すぐ作成したい
```bash
# 1. 手順書を確認
cat docs/deployment/stg-environment-setup.md

# 2. Railway CLI で環境作成
railway environment new staging

# 詳細は stg-environment-setup.md を参照
```

### Railway移行を実行したい
```bash
# 1. チェックリストを確認
cat docs/deployment/railway-deployment-checklist.md

# 2. 移行前準備
# 詳細は railway-deployment-checklist.md を参照
```

## ⚠️ 注意事項

### STG環境作成のベストプラクティス
- **月初作成推奨**: 月の初め（1-3日）での作成で最大活用
- **App Sleep活用**: 自動コスト削減（$1-3/月）
- **不要時は即座削除**: 日割り課金で無駄なコスト回避

### Railway移行時の重要ポイント
- **本番環境のバックアップ必須**
- **環境変数の正確な移行**
- **DNS設定の適切な更新**

## 🔗 関連ドキュメント

- [プロジェクト全体指示](../../CLAUDE.md) - AI開発支援用の全体設定
- [開発環境ドキュメント](../development/) - ローカル開発環境セットアップ
- [運用ドキュメント](../operations/) - バックアップ・監視設定