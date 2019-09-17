FROM python:3.6.8-slim

EXPOSE 5000
RUN mkdir /app
WORKDIR /app
ADD . .
RUN pip install -r requirements.txt && chmod +x /app/api.py

CMD python /app/api.py
