echo "Stopping old containers..."
docker compose down -v --remove-orphans

echo "Starting Docker containers..."
docker compose up -d --build

echo "All services are up!"
# echo "Launching Mandator GUI..."
# sleep 5

# java -jar path/to/mandator-gui/target/mandator-gui.jar &

# echo "GUI is up!"