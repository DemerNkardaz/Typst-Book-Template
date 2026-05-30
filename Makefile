.PHONY: all build

all: build

build:
	python3 build/build.py --mode=$(m) --as=$(as)

print:
	python3 build/build.py --mode=print --as=$(as)
