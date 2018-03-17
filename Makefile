build-latest-image:
	find . -type d -name __pycache__ -exec rm -r {} \+
	docker build --tag zetanote:latest .

start-latest-container:
	mkdir -p `pwd`/data
	docker run -it --env-file ./.env -p 8964:8964 --rm -v `pwd`:/app -v `pwd`/data:/data zetanote:latest bash

start-webserver:
	gunicorn zetanote.wsgi:app -b 0.0.0.0:8964 --log-file -

download-published-image:
	docker pull soasme/zetanote

start-published-container: download-published-image
	docker run --env-file ./.env.docker -p 8964:8964 -it --rm -v `pwd`/data:/data -e ZETANOTE_DATA=/data soasme/zetanote

start:
	docker-compose up -d

stop:
	docker-compose stop

logs:
	docker-compose logs -f --tail="100"

attach:
	docker exec -it zetanote_web_1 bash
