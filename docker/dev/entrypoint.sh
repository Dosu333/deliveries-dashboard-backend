#!/bin/sh

if [ "$DEBUG" = 1 ]
then
    echo "Waiting for database response..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
        sleep 0.1
    done

    echo "Database Started!"

fi

# python manage.py flush --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
# python manage.py collectstatic --no-input --clear
rm celerybeat.pid

exec "$@"