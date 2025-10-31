#!/usr/bin/env python3
"""
Build script for KAI Agent Docker sandbox.

This script builds the Docker image required for secure code execution.
Run this script before using the agent's code execution features.

Usage:
    python build_sandbox.py
"""

import os
import sys

import docker


def build_sandbox_image():
    """Build the Docker sandbox image."""
    print("=" * 60)
    print("KAI Agent Sandbox Builder")
    print("=" * 60)
    print()

    # Check if Docker is available
    try:
        client = docker.from_env()
        print("✓ Docker is running")
    except docker.errors.DockerException as e:
        print("✗ Docker is not available")
        print(f"  Error: {e}")
        print()
        print("Please install Docker and make sure it's running:")
        print("  - Windows/Mac: https://www.docker.com/products/docker-desktop")
        print("  - Linux: https://docs.docker.com/engine/install/")
        return False

    # Get the sandbox directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sandbox_dir = os.path.join(script_dir, "sandbox")

    if not os.path.exists(sandbox_dir):
        print(f"✗ Sandbox directory not found: {sandbox_dir}")
        return False

    print(f"✓ Sandbox directory found: {sandbox_dir}")
    print()

    # Build the image
    image_name = "kai_agent_sandbox"
    print(f"Building Docker image '{image_name}'...")
    print("This may take a few minutes on first build...")
    print()

    try:
        # Build the image
        image, build_logs = client.images.build(
            path=sandbox_dir,
            tag=image_name,
            rm=True,  # Remove intermediate containers
            forcerm=True  # Always remove intermediate containers
        )

        # Print build logs
        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())
            elif 'error' in log:
                print(f"ERROR: {log['error']}")

        print()
        print("=" * 60)
        print(f"✓ Successfully built image '{image_name}'")
        print("=" * 60)
        print()
        print("You can now use the agent's code execution features!")
        print()

        # Show image info
        print("Image details:")
        print(f"  ID: {image.id}")
        print(f"  Tags: {image.tags}")
        print(f"  Size: {image.attrs['Size'] / (1024 * 1024):.2f} MB")
        print()

        return True

    except docker.errors.BuildError as e:
        print()
        print("=" * 60)
        print("✗ Build failed")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Build log:")
        for log in e.build_log:
            if 'stream' in log:
                print(log['stream'].strip())
            elif 'error' in log:
                print(f"ERROR: {log['error']}")
        return False

    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Unexpected error")
        print("=" * 60)
        print(f"Error: {e}")
        return False


def main():
    """Main entry point."""
    success = build_sandbox_image()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
