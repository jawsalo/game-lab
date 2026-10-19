ENV ?= example
VALUES := deploy/environments/$(ENV).yaml
CHART := deploy/chart

.PHONY: validate validate-catalog endpoints helm-lint helm-render

validate:
	python3 scripts/validate.py
	python3 scripts/validate-grim-dawn-catalog.py

validate-catalog:
	python3 scripts/validate-grim-dawn-catalog.py

endpoints:
	python3 scripts/validate.py --environment $(VALUES) --print-endpoints

helm-lint:
	helm lint $(CHART) -f $(VALUES)

helm-render:
	mkdir -p rendered
	helm template game-lab $(CHART) -f $(VALUES) > rendered/$(ENV).yaml
