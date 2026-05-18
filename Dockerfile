FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app

EXPOSE 8000

COPY <<-"EOF" /usr/local/bin/start.sh
#!/bin/sh
echo "Running migrations..."
for i in $(seq 1 30); do
  alembic upgrade head && break
  echo "Migration attempt $i failed, retrying in 2s..."
  sleep 2
done
echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF
RUN chmod +x /usr/local/bin/start.sh

CMD ["start.sh"]
