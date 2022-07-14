.PHONY: lint pyenv test-local

gitroot = ${shell git rev-parse --show-toplevel}
repo = ${notdir ${gitroot}}
PROJECT_NAME ?= ${repo}
python_version = 3.9.5
VIRTUAL_ENV=${shell pyenv root}/versions/${python_version}/envs/${PROJECT_NAME}-integration-tests

TEST_CONTAINER = ${PROJECT_NAME:-api=}-integration-tests

lint: ## Run `black`, `isort`, and `mypy` over the integration tests.
lint:
	black .
	isort --profile black .
	mypy clients/ helpers/ steps/ --ignore-missing-imports --disallow-untyped-defs

test-local: ## Builds docker containers for the microservice and the integration tests. Other containers are pulled from Azure and Docker repositories.
## Note that before running this command you must be logged in to an Azure account with access to the Sensyne container repository.
## Use the `az acr login -n sensynehealth` command before running the tests or whenever your login expires.
test-local: lint
	docker-compose pull
	docker-compose build
	docker-compose up --no-start --force-recreate
	docker-compose run ${TEST_CONTAINER}
	docker-compose down

pyenv: ## Creates a local Python virtual environment for the integration tests.
pyenv:
	pyenv virtualenv ${python_version} ${PROJECT_NAME}-integration-tests
	pyenv local ${PROJECT_NAME}-integration-tests
	pip install -r requirements.txt
