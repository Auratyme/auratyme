# --- Script to monitor scheduler logs in the Docker container ---

CONTAINER_ID=$(docker ps | grep schedules-ai | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
    echo "Container schedules-ai not found. Make sure the container is running."
    exit 1
fi

echo "Monitoring scheduler logs in container $CONTAINER_ID..."
echo "Press Ctrl+C to exit."

docker exec -it $CONTAINER_ID tail -f /app/scheduler.log
