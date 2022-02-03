test:
	pytest --tb=short

black:
	black $$(find * -name '*.py')
