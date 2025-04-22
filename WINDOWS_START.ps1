Write-Host "Stopping old containers..."
docker compose down -v --remove-orphans

Write-Host "Starting Docker containers..."
docker compose up -d --build

# Write-Host "Opening Producer in IDE..."
# code ./producer

# Write-Host "Opening User in IDE..."
# code ./user

Write-Host "All services are up!"
