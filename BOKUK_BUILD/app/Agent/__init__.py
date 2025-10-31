"""
KAI Agent - Autonomous AI Expert System
========================================

An intelligent agent system with dual expertise:
1. Renewable Energy Consulting (Photovoltaics & Heat Pumps)
2. Software Architecture & Development

Features:
- Knowledge base search with FAISS vector store
- Outbound calling with ElevenLabs voice synthesis
- Secure code execution in Docker sandbox
- File system operations in isolated workspace
- Web search integration
- Automated testing with pytest
- ReAct pattern for autonomous reasoning

Author: Bokuk2 Development Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Bokuk2 Development Team"

# Import main components for easy access
from agent.agent_core import AgentCore
from agent.errors import (
    AgentError,
    APIError,
    ConfigurationError,
    DockerError,
    ExecutionError,
    KnowledgeBaseError,
    ToolError,
)

__all__ = [
    "AgentCore",
    "AgentError",
    "ConfigurationError",
    "ExecutionError",
    "APIError",
    "DockerError",
    "KnowledgeBaseError",
    "ToolError",
]
