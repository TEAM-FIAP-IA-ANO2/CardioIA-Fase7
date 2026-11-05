.PHONY: install test api web mobile docker zip
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
api:
	uvicorn cardioia.api:app --reload --port 8000
web:
	cd web && npm install && npm run dev
mobile:
	cd mobile && npm install && npx expo start
docker:
	docker compose up --build
zip:
	python scripts/package_release.py
