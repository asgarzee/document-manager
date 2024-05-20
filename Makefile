createsuperuser:
	docker compose run app python manage.py createsuperuser

test:
	docker compose run app pytest

make-migrations:
	docker compose run app python manage.py makemigrations

format:
	docker compose run app ruff format

lint:
	docker compose run app ruff check

lint-fix:
	docker compose run app ruff check --fix


