web: gunicorn app:app
release: flask shell <<< 'from app import init_db; init_db()'
