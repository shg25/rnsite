# 開発環境ドキュメント

このディレクトリには、ローカル開発環境のセットアップや開発手順に関するドキュメントが含まれています。

## 📋 ドキュメント一覧（今後追加予定）

### ローカル開発環境
- **local-setup.md** - ローカル開発環境のセットアップ手順
- **testing.md** - テスト実行・デバッグ手順
- **coding-standards.md** - コーディング規約・ベストプラクティス

## 🏗️ 基本的な開発環境セットアップ

現在、開発環境の詳細は [CLAUDE.md](../../CLAUDE.md) に記載されています。

### 初回セットアップ（概要）
```bash
# 1. local_settings.py 作成（必須）
# ルートディレクトリに local_settings.py を作成

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

# テスト実行
python manage.py test

# Django shell起動
python manage.py shell
```

## 📝 開発フロー

### ブランチ戦略
```bash
# 開発フロー
develop → staging → main

# 基本的な開発サイクル
1. develop ブランチで開発
2. STG環境でテスト
3. main ブランチにマージ
4. 本番環境デプロイ
```

## 🔗 関連ドキュメント

- [CLAUDE.md](../../CLAUDE.md) - プロジェクト全体の開発指針
- [STG環境セットアップ](../deployment/STG_ENVIRONMENT_SETUP.md) - テスト環境構築
- [Railway移行ガイド](../deployment/RAILWAY_DEPLOYMENT_CHECKLIST.md) - デプロイ手順

## 🚧 TODO

このディレクトリは今後以下のドキュメントで充実させる予定です：

- [ ] ローカル開発環境詳細セットアップ
- [ ] テスト戦略・実行手順
- [ ] コードレビューガイドライン  
- [ ] デバッグ・トラブルシューティング
- [ ] パフォーマンス最適化ガイド