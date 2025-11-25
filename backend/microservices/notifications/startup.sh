#!/bin/sh

docker compose up -d --build
docker compose exec notifications npx drizzle-kit push --force
docker compose restart notifications