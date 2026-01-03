# PowerShell build script for KAI Agent Docker sandbox (Windows)
# This script builds the Docker image required for secure code execution

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "KAI Agent Sandbox Builder (Windows)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed"
    }
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not available" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker Desktop for Windows:" -ForegroundColor Yellow
    Write-Host "  https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if Docker daemon is running
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon not running"
    }
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

# Get the sandbox directory
$sandboxDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if Dockerfile exists
if (-not (Test-Path "$sandboxDir\Dockerfile")) {
    Write-Host "✗ Dockerfile not found in: $sandboxDir" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dockerfile found: $sandboxDir\Dockerfile" -ForegroundColor Green
Write-Host ""

# Build the image
$imageName = "kai_agent_sandbox"
Write-Host "Building Docker image '$imageName'..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first build..." -ForegroundColor Yellow
Write-Host ""

try {
    # Build with progress output
    docker build -t $imageName $sandboxDir
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed"
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✓ Successfully built image '$imageName'" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    
    # Show image info
    Write-Host "Image details:" -ForegroundColor Cyan
    $imageInfo = docker images $imageName --format "{{.ID}}\t{{.Size}}\t{{.CreatedAt}}"
    $parts = $imageInfo -split '\t'
    Write-Host "  ID: $($parts[0])" -ForegroundColor White
    Write-Host "  Size: $($parts[1])" -ForegroundColor White
    Write-Host "  Created: $($parts[2])" -ForegroundColor White
    Write-Host ""
    
    # Test the image
    Write-Host "Testing image..." -ForegroundColor Yellow
    $testResult = docker run --rm $imageName python -c "print('Image test successful')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Image test passed: $testResult" -ForegroundColor Green
    } else {
        Write-Host "✗ Image test failed" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "You can now use the agent's code execution features!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run tests: python Agent\test_execution_tools.py" -ForegroundColor White
    Write-Host "  2. Or run: python Agent\test_sandbox_complete.py" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "✗ Build failed" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
