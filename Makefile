PYTHON ?= .venv/bin/python

lint: 
	pre-commit run -a 

install:
	python3.10 -m venv .venv
	. .venv/bin/activate
	$(PYTHON) -m pip install -r requirements.txt

jup:
	. .venv/bin/activate
	$(PYTHON) -m jupyterlab

jup-darwin:
	. .venv/bin/activate
	$(PYTHON) -m jupyterlab --app-dir=/opt/homebrew/share/jupyter/lab
