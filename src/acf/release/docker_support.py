"""
Atmospheric Complexity Framework (ACF)

Docker & Containerization Support Module
"""

from typing import Any


class DockerSupport:
    """Générateur de configurations Docker et Docker-Compose pour ACF."""

    @classmethod
    def generate_docker_manifests(cls) -> dict[str, Any]:
        return {
            "dockerfile": "Dockerfile.production",
            "docker_compose": "docker-compose.yml",
            "base_image": "nvidia/cuda:12.4.0-devel-ubuntu22.04",
        }
