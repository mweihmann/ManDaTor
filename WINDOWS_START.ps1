Write-Host "Stopping old containers..."
docker compose down -v --remove-orphans

Write-Host "Starting Docker containers..."
docker compose up -d --build

Write-Host "All services are up!"
# Write-Host "Launching Mandator GUI..."
# Start-Sleep -Seconds 5

# Start-Process "java" "-jar path\to\mandator-gui\target\mandator-gui.jar"

# Write-Host "GUI is up!"
