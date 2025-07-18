web: gunicorn app:app
release: echo "from app import init_db; init_db()" | flask shell
