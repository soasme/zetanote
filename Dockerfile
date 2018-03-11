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
CMD bash
