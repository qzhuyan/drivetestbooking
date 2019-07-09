all: runtime run

runtime: venv requirements

venv:
	virtualenv venv

requirements:
	. venv/bin/activate && pip install -r requirements.txt


run:
	venv/bin/python bot.py
