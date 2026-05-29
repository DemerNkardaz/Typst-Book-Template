.PHONY: all build

all: build

build:
	python3 build.py --mode=$(m)

print:
	python3 build.py --mode=print
