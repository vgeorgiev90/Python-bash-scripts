FROM python:2.7

RUN pip install flask jsonpatch pyyaml && mkdir -p /app/sidecars /app/ssl

WORKDIR /app

COPY ./webhook/server.py .

RUN chmod +x /app/server.py

EXPOSE 443

ENTRYPOINT python /app/server.py
