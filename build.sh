#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
# Free Render plan has no shell: create the admin from env vars (skipped if it exists)
python manage.py createsuperuser --no-input || true
