echo "Stopping old containers..."
docker compose down -v --remove-orphans

echo "Starting Docker containers..."
docker compose up -d --build

# echo "Opening Producer in IDE..."
# code ./producer

# echo "Opening User in IDE..."
# code ./user

echo "All services are up!"