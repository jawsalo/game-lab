ENV ?= example
VALUES := deploy/environments/$(ENV).yaml
CHART := deploy/chart

.PHONY: validate endpoints helm-lint helm-render

validate:
	python3 scripts/validate.py

endpoints:
	python3 scripts/validate.py --environment $(VALUES) --print-endpoints

helm-lint:
	helm lint $(CHART) -f $(VALUES)

helm-render:
	mkdir -p rendered
	helm template game-lab $(CHART) -f $(VALUES) > rendered/$(ENV).yaml
