FROM python:3.7

COPY requirements.txt /requirements.txt
COPY handler.py /handler.py
RUN mkdir /root/.aws && pip install -r /requirements.txt
CMD kopf run --standalone /handler.py
