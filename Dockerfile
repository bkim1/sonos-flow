FROM python:3.7.0-alpine

RUN adduser -D flo

WORKDIR /home/flo

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY flo.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP flo.py

RUN chown -R flo:flo ./
USER flo

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]