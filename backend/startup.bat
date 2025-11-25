docker compose up -d --build

docker compose exec schedules npm run db:push -w schedules
docker compose exec notifications npm run db:push -w notifications
docker compose exec users npm run db:push -w users