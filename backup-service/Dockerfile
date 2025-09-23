FROM node:18-alpine

# PostgreSQL v17サーバー対応：v17専用クライアント→最新安定版→v16の順でフォールバック
RUN apk update && \
    (apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main postgresql17-client || \
     apk add --no-cache postgresql-client || \
     apk add --no-cache postgresql16-client)

WORKDIR /app

# 依存関係をインストール
COPY package.json ./
RUN npm install --production

# アプリケーションファイルをコピー
COPY smart-backup.js ./
COPY cron-backup.js ./

# 実行権限を設定
RUN chmod +x smart-backup.js

# デフォルトコマンド（cronスケジューラーを実行）
CMD ["node", "cron-backup.js"]