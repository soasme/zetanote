build-latest-image:
	find . -type d -name __pycache__ -exec rm -r {} \+
	docker build --tag zetanote:latest .

start-latest-container:
	mkdir -p `pwd`/data
	docker run -it --rm -v `pwd`/data:/data -e ZETANOTE_DATA=/data zetanote:latest
