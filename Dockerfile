FROM python:3.9-slim

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# staticfilesディレクトリを事前作成
RUN mkdir -p staticfiles

# アプリケーションを起動
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput -v 2 && ls -la staticfiles/ && gunicorn rnsite.wsgi --bind 0.0.0.0:$PORT"]