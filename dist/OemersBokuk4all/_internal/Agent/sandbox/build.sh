#!/bin/bash
# Bash build script for KAI Agent Docker sandbox (Linux/Mac)
# This script builds the Docker image required for secure code execution

echo "============================================================"
echo "KAI Agent Sandbox Builder (Linux/Mac)"
echo "============================================================"
echo ""

# Check if Docker is running
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "✗ Docker is not installed"
    echo ""
    echo "Please install Docker:"
    echo "  - Mac: https://docs.docker.com/desktop/install/mac-install/"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo "✓ Docker is installed: $(docker --version)"

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo "✗ Docker daemon is not running"
    echo ""
    echo "Please start Docker:"
    echo "  - Mac: Start Docker Desktop"
    echo "  - Linux: sudo systemctl start docker"
    echo ""
    exit 1
fi

echo "✓ Docker daemon is running"
echo ""

# Get the sandbox directory
SANDBOX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Dockerfile exists
if [ ! -f "$SANDBOX_DIR/Dockerfile" ]; then
    echo "✗ Dockerfile not found in: $SANDBOX_DIR"
    exit 1
fi

echo "✓ Dockerfile found: $SANDBOX_DIR/Dockerfile"
echo ""

# Build the image
IMAGE_NAME="kai_agent_sandbox"
echo "Building Docker image '$IMAGE_NAME'..."
echo "This may take a few minutes on first build..."
echo ""

if docker build -t "$IMAGE_NAME" "$SANDBOX_DIR"; then
    echo ""
    echo "============================================================"
    echo "✓ Successfully built image '$IMAGE_NAME'"
    echo "============================================================"
    echo ""
    
    # Show image info
    echo "Image details:"
    IMAGE_ID=$(docker images "$IMAGE_NAME" --format "{{.ID}}")
    IMAGE_SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
    IMAGE_CREATED=$(docker images "$IMAGE_NAME" --format "{{.CreatedAt}}")
    echo "  ID: $IMAGE_ID"
    echo "  Size: $IMAGE_SIZE"
    echo "  Created: $IMAGE_CREATED"
    echo ""
    
    # Test the image
    echo "Testing image..."
    if docker run --rm "$IMAGE_NAME" python -c "print('Image test successful')"; then
        echo "✓ Image test passed"
    else
        echo "✗ Image test failed"
    fi
    echo ""
    
    echo "You can now use the agent's code execution features!"
    echo ""
    echo "Next steps:"
    echo "  1. Run tests: python Agent/test_execution_tools.py"
    echo "  2. Or run: python Agent/test_sandbox_complete.py"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "✗ Build failed"
    echo "============================================================"
    echo ""
    exit 1
fi
