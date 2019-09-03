FROM python:3.6

ENV DJANGO_SETTINGS_MODULE photo_verification.settings.development

# Install requirements
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add application
ADD . /app
WORKDIR /app

EXPOSE 8000
CMD gunicorn photo_verification.wsgi --bind=0.0.0.0:8000 --workers ${WORKER_COUNT:-2}
