install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt

test:
	PYTHONPATH=src pytest -v

format:
	black src tests

lint:
	ruff check src tests

typecheck:
	mypy src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
