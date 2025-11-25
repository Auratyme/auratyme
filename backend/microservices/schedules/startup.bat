docker compose up -d --build
docker compose exec schedules npx drizzle-kit push --force
docker compose restart schedules