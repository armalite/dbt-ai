include *.mk

.PHONY: build dist test release publish-test

PACKAGE_NAME=dbt-ai
testpypi = https://test.pypi.org/legacy/


clean-build:
	rm -rf dist

build-image:
	docker build -t dbt-ai-deployer .

build:
	pip install --upgrade build

dist:
	python -m build

publish-test: clean-build build dist
	@twine upload --verbose --repository-url https://test.pypi.org/legacy/ --username $(PYPI_USERNAME) --password $(PYPI_PASSWORD_TEST) dist/*


publish-prod: clean-build build dist
	@twine upload --verbose --username $(PYPI_USERNAME) --password $(PYPI_PASSWORD_PROD) dist/*