"""
Atmospheric Complexity Framework (ACF)

Docker & Containerization Support Module
"""

from typing import Any


class DockerSupport:
    """Générateur de configurations Docker et Docker-Compose pour ACF."""

    @classmethod
    def generate_docker_manifests(cls) -> dict[str, Any]:
        """
        NOTE (correction, 2026-09-06 Tier E sweep - same pattern as
        this module's already-fixed CloudSupport.get_cloud_config()):
        no Dockerfile/docker-compose.yml is written to disk here -
        these are planned target filenames/base image, not a report of
        real generated artifacts. Verified no docker/docker-compose
        invocation or file write exists anywhere in this method.
        """
        return {
            "planned_dockerfile": "Dockerfile.production",
            "planned_docker_compose": "docker-compose.yml",
            "planned_base_image": "nvidia/cuda:12.4.0-devel-ubuntu22.04",
            "status": "NOT_GENERATED_NO_MANIFEST_WRITTEN",
            "is_real_data": False,
        }
