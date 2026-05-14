$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$haConfigPath = Join-Path $repoRoot "docker\ha_config"
$integrationPath = Join-Path $repoRoot "custom_components\hacs_marstek_venus_e"
$imageName = "marstek-ha"
$containerName = "homeassistant"

# Build from the repository root so the Dockerfile can copy custom_components.
podman build -f (Join-Path $repoRoot "docker\Dockerfile") -t $imageName $repoRoot

# Use port mapping on Windows/Podman so Home Assistant is reachable at http://localhost:8123.
# The integration is mounted separately because mounting /config hides files copied there by the image.
podman run -d --replace `
  --name $containerName `
  -p 8123:8123 `
  -e TZ=Europe/Brussels `
  -v "${haConfigPath}:/config" `
  -v "${integrationPath}:/config/custom_components/hacs_marstek_venus_e" `
  $imageName

Write-Host "Home Assistant is starting at http://localhost:8123"
