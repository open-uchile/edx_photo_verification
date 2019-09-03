FROM python:3.6

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app
WORKDIR /app

CMD gunicorn photo_verification.wsgi --bind=0.0.0.0:8000 --workers ${WORKER_COUNT:-2}
