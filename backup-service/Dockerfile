FROM node:18-alpine

# PostgreSQL 17対応のため、最新のPostgreSQLクライアントをインストール
RUN apk update && apk add --no-cache postgresql-client || apk add --no-cache postgresql16-client

WORKDIR /app

# 依存関係をインストール
COPY package.json ./
RUN npm install --production

# アプリケーションファイルをコピー
COPY smart-backup.js ./

# cronジョブとして実行する場合
COPY cron-backup.js ./

# 実行権限を付与
RUN chmod +x smart-backup.js

# デフォルトコマンド（cronまたは単発実行）
CMD ["node", "cron-backup.js"]