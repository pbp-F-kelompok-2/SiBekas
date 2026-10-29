release: python manage.py migrate --noinput && python manage.py bootstrap_catalog && python manage.py collectstatic --noinput
web: gunicorn sibekas.wsgi:application --bind 0.0.0.0:$PORT
