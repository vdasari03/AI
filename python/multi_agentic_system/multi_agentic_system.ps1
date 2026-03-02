# Base Path
$basePath = "C:\Interview\media_driven\python\multi_agentic_system\weather-agent-system"

# Folder Structure
$folders = @(
    "$basePath\src",
    "$basePath\src\agents",
    "$basePath\src\orchestrator",
    "$basePath\src\models",
    "$basePath\src\services",
    "$basePath\src\config",
    "$basePath\src\utils",
    "$basePath\tests",
    "$basePath\tests\unit",
    "$basePath\tests\integration",
    "$basePath\tests\fixtures"
)

# File Structure
$files = @(
    # src root
    "$basePath\src\__init__.py",

    # agents
    "$basePath\src\agents\__init__.py",
    "$basePath\src\agents\base_agent.py",
    "$basePath\src\agents\geolocation_agent.py",
    "$basePath\src\agents\temperature_agent.py",
    "$basePath\src\agents\time_agent.py",

    # orchestrator
    "$basePath\src\orchestrator\__init__.py",
    "$basePath\src\orchestrator\weather_orchestrator.py",

    # models
    "$basePath\src\models\__init__.py",
    "$basePath\src\models\data_models.py",

    # services
    "$basePath\src\services\__init__.py",
    "$basePath\src\services\weather_service.py",
    "$basePath\src\services\geocoding_service.py",

    # config
    "$basePath\src\config\__init__.py",
    "$basePath\src\config\settings.py",

    # utils
    "$basePath\src\utils\__init__.py",
    "$basePath\src\utils\logger.py",

    # tests
    "$basePath\tests\__init__.py",
    "$basePath\tests\unit\test_agents.py",
    "$basePath\tests\unit\test_orchestrator.py",
    "$basePath\tests\integration\test_weather_flow.py",
    "$basePath\tests\fixtures\mock_data.py",

    # root files
    "$basePath\requirements.txt",
    "$basePath\.env.example",
    "$basePath\pytest.ini",
    "$basePath\README.md"
)

# Create Folders
foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Created folder: $folder"
    }
}

# Create Files
foreach ($file in $files) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
        Write-Host "Created file: $file"
    }
}

Write-Host "`nWeather Agent System structure created successfully!"