FROM python:3-alpine as build

# Setup project
ADD ./ /app

# Install Python dependencies
RUN pip install --no-cache /app

FROM python:3-alpine

RUN apk add --no-cache curl bash

COPY --from=build /usr/local /usr/local

WORKDIR /app

EXPOSE 8964

# https://github.com/gliderlabs/docker-alpine/blob/master/docs/usage.md

# Run web process by default.
CMD gunicorn zetanote.wsgi:app -b 0.0.0.0:8964 --workers 8 --error-logfile /var/log/error.log --access-logfile /var/log/access.log
