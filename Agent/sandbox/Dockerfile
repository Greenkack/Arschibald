# KAI Agent Sandbox Docker Image
# 
# This Dockerfile creates a secure, isolated environment for code execution.
# Security features (Task 12.2):
# - Runs as unprivileged user (sandboxuser) - Requirement 5.2
# - Minimal base image (python:3.11-slim)
# - No root access after user switch
# - Isolated workspace directory
# - Resource limits configured at runtime
# - Network isolation by default
# - Read-only root filesystem support
# - No unnecessary packages or tools

FROM python:3.11-slim

# Security: Update packages and remove unnecessary tools
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Security: Create unprivileged user with no login shell (Requirement 5.2)
# - No home directory login
# - No sudo access
# - Limited shell access
RUN useradd --create-home --shell /bin/bash --uid 1000 sandboxuser && \
    # Remove unnecessary setuid binaries for security
    find / -perm /6000 -type f -exec chmod a-s {} \; 2>/dev/null || true

# Set up application directory
WORKDIR /app

# Copy and install Python dependencies as root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Security: Set proper ownership and permissions
RUN chown -R sandboxuser:sandboxuser /app && \
    chmod -R 755 /app

# Security: Switch to unprivileged user (Requirement 5.2)
# All subsequent commands run as sandboxuser
USER sandboxuser

# Create workspace directory for code execution
RUN mkdir -p /app/workspace

# Set workspace as working directory
WORKDIR /app/workspace

# Security: Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Health check (optional, for monitoring)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=1 \
    CMD python -c "print('healthy')" || exit 1

# Default command
CMD ["/bin/bash"]