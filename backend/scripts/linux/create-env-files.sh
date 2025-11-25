# list of microservices with subfolders that need env files
services=(
  "infrastructure/broker"
  "infrastructure/reverse-proxy"
  "microservices/api-gateway"
  "microservices/jobs"
  "microservices/jobs/database"
  "microservices/notifications"
  "microservices/notifications/database"
  "microservices/schedules"
  "microservices/schedules/database"
  "microservices/schedules-ai/core"
  "microservices/schedules-ai/database"
  "microservices/schedules-ai/gateway"
  "microservices/users"
  "microservices/users/database"
)

for service in "${services[@]}"; do
  if [ -f "./$service/.env.example" ]; then
    cp "./$service/.env.example" "./$service/.env"
    echo "Created .env for $service"
  else
    echo "⚠️  Missing .env.example for $service"
  fi
done
