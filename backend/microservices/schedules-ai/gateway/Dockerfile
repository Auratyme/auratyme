ARG NGINX_VERSION=1.29

FROM nginx:${NGINX_VERSION}-alpine AS base

FROM base AS dev

RUN apk add curl

FROM base AS prod