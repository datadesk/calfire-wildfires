.PHONY: lint test ship

lint:
	pipenv run flake8 ./

test:
	pipenv run coverage run test.py
	pipenv run coverage report -m


scrape:
	pipenv run calfirewildfires all-fires > data/all.json
	pipenv run calfirewildfires active-fires > data/active.json

ship:
	rm -rf build/
	rm -rf dist/
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/* --skip-existing
