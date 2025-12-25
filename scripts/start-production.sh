#!/bin/bash
# Start production server manually (for testing)

set -e
cd /home/astre/command-center/testhome/testhome-visualizer
source venv/bin/activate
source .env

echo "Building frontend..."
cd frontend && npm run build && cd ..

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --config gunicorn.conf.py pools_project.wsgi:application
