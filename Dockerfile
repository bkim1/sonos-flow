FROM python:3.7.0-alpine

RUN adduser -D flow

WORKDIR /home/flow

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY flo.py boot.sh ./
COPY vars.env ./
RUN chmod +x boot.sh

ENV FLASK_APP flow.py

RUN chown -R flow:flow ./
USER flow

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]