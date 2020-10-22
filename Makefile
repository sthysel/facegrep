.PHONY: tests clean quality

.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep --no-filename -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


tests: build-devbox ## Run all the tests
	$(call execute_cmd) run pytest -c pyproject.toml -s --log-cli-level=10  --junitxml=./junit_report.xml

quality: build-devbox  ## Analyze code quality
	$(call execute_cmd) run black -l 200 --target-version py37 facegrep
	$(call execute_cmd) run isort --recursive ./{{cookiecutter.app_name}} -vvv
	$(call execute_cmd) run flake8 facegrep --ignore=E501

clean: ## Remove build artifacts
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -f junit_report.xml
	rm -Rf .coverage
	rm -Rf dist
	rm -Rf *.egg-info
	rm -Rf .pytest_cache

# if the first argument is "poetry"...
ifeq (poetry,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "poetry"
  POETRY_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(POETRY_ARGS):dummy;@:)
endif

build-devbox:  ## Build dev container
	docker build -t facegrep-devbox -f Dockerfile.dev .

poetry: build-devbox ## Run poetry command in dev container
	$(call execute_cmd) $(POETRY_ARGS)

distclean: build-buildozer ## Clean out build container
	docker run --interactive --tty --rm -v buildozer_home:/home/user/.buildozer  --volume ${CURDIR}:/home/user/hostcwd facegrep-buildozer distclean

build-buildozer: ## Build using buildozer
	docker build -t facegrep-buildozer -f Dockerfile .

deploy: build-buildozer ## Deploy android application
	docker run -it \
	  --privileged \
	  --volume /dev/bus/usb:/dev/bus/usb \
	  --volume buildozer_home:/root/.buildozer \
	  --volume gradle_cache:/root/.gradle \
	  --volume ${CURDIR}:/home/user/hostcwd \
	  facegrep-buildozer android debug deploy run logcat

build-ide: ## Build developer container for IDE
	docker build -t facegrep-ide -f Dockerfile.ide .

run-ide: ## vscode IDE support
	docker run -it -p 127.0.0.1:8080:8080 -v "${CURDIR}:/home/coder/project" facegrep-ide --auth none &
	xdg-open "http://localhost:8080/?folder=vscode-remote%3A%2F%2Flocalhost%3A8080%2Fhome%2Fcoder%2Fproject" &


define execute_cmd
	docker run -i -v ${CURDIR}:/opt/facegrep --env-file .env facegrep-devbox $(1)
endef
