.PHONY: install init-db seed test test-all run-batch generate-artifacts clean

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements.txt

init-db:
	$(PYTHON) -m specforge.db.init_db

seed:
	$(PYTHON) scripts/seed_evaluation_dataset.py

test:
	$(PYTHON) -m pytest -v -m "not integration" --cov=specforge

test-all:
	$(PYTHON) -m pytest -v --cov=specforge

run-batch:
	$(PYTHON) -m specforge.experiments.batch_runner

generate-artifacts:
	$(PYTHON) -m specforge.thesis_export.generate_thesis_artifacts

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov thesis_artifacts
