install:
	pip install -r requirements.txt

check:
	flake8

black:
	black .

isort:
	isort . --profile black

format:
	isort . --profile black
	black .

test:
	pytest tests/

req:
	pip3 freeze > requirements.txt