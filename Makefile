format:
	black . -l 79

install:
	pip install -e .[dev]

all: install format

documentation:
	jb clean docs
	jb build docs
