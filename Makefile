.PHONY: test ship

test:
	flake8 ./
	coverage run test.py
	coverage report -m


ship:
	rm -rf build/
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing


fires:
	python -c "import calfire_wildfires; calfire_wildfires.get_fires()"
