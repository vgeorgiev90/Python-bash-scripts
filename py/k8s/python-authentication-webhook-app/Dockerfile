FROM python:2.7

RUN mkdir -p /app/log /app/ssl
WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

## ssl certs must be signed by kubernetes ca and must be mounted to /app/ssl/tls.crt /app/ssl/tls.key
ENTRYPOINT /app/app/auth-server.py
