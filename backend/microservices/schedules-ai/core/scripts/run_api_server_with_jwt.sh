echo "Starting API server with JWT authentication enabled..."

export ENABLE_JWT_AUTH=true
export DISABLE_DB=true

python -m api.server

echo "API server stopped."
