ARG NGINX_VERSION=1.29

FROM nginx:${NGINX_VERSION}-alpine AS base

COPY ./etc/nginx/nginx.conf /etc/nginx/
COPY ./etc/nginx/proxy_params.conf /etc/nginx/

FROM base AS dev

RUN apk add curl

FROM base AS prod