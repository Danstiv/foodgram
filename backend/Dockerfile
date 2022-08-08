FROM python:3.7-slim
WORKDIR /app
copy ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./ .
CMD python manage.py migrate && \
python manage.py collectstatic --noinput && \
gunicorn backend.wsgi:application --bind 0:8000
