build-latest-image:
	find . -type d -name __pycache__ -exec rm -r {} \+
	docker build --tag zetanote:latest .

start-latest-container:
	mkdir -p `pwd`/data
	docker run -it -p 8964:8964 --rm -v `pwd`/data:/data -e ZETANOTE_DATA=/data zetanote:latest

download-published-image:
	docker pull soasme/zetanote

start-published-container: download-published-image
	docker run --env-file ./.env.docker -p 8964:8964 -it --rm -v `pwd`/data:/data -e ZETANOTE_DATA=/data soasme/zetanote
