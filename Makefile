ENV ?= example
VALUES := deploy/environments/$(ENV).yaml
CHART := deploy/chart

.PHONY: validate validate-catalog test-api endpoints helm-lint helm-render

validate:
	python3 scripts/validate.py
	python3 scripts/validate-grim-dawn-catalog.py
	python3 -m unittest discover -s scripts/tests -v
	python3 -m unittest discover -s apps/api/tests -v

validate-catalog:
	python3 scripts/validate-grim-dawn-catalog.py

test-api:
	python3 -m unittest discover -s apps/api/tests -v

endpoints:
	python3 scripts/validate.py --environment $(VALUES) --print-endpoints

helm-lint:
	helm lint $(CHART) -f $(VALUES)

helm-render:
	mkdir -p rendered
	helm template game-lab $(CHART) -f $(VALUES) > rendered/$(ENV).yaml
