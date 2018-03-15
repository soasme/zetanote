FROM python:3-alpine as build

# Setup project
COPY ./ /app/

# Install Python dependencies
RUN pip install --no-cache /app

FROM python:3-alpine

COPY --from=build /usr/local /usr/local

EXPOSE 8964

RUN apk add --no-cache curl bash
# https://github.com/gliderlabs/docker-alpine/blob/master/docs/usage.md

# Run web process by default.
CMD gunicorn zetanote.wsgi:app -b 0.0.0.0:8964 --workers 8 --error-logfile /var/log/error.log --access-logfile /var/log/access.log
