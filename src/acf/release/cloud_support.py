"""
Atmospheric Complexity Framework (ACF)

Cloud Infrastructure Support Module (AWS, GCP, Azure)
"""

from typing import Any


class CloudSupport:
    """Intégration et provisionnement pour cloud (AWS EKS, GCP GKE, Azure AKS)."""

    @classmethod
    def get_cloud_config(cls) -> dict[str, Any]:
        """
        NOTE (correction): supported_clouds itself is a genuine static
        list of intended target platforms, but "status": "CLOUD_READY"
        implied live, operational cloud integration - no cloud SDK
        (boto3, google-cloud-*, azure-mgmt-*) is a declared dependency
        of this project and no provisioning code exists. Now clarifies
        this is a planned/target list, not an active integration.
        """
        return {
            "planned_cloud_targets": ["AWS", "GCP", "Azure"],
            "status": "NOT_INTEGRATED_NO_CLOUD_SDK_CONNECTED",
            "is_real_data": False,
        }
