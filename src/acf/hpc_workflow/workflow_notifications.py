"""HPC Workflow Notifications & Events (ACF-HPC-104)."""

from typing import Any


class WorkflowNotifications:
    """Generates alerts for forecast finished, failed, restart, or completed.

    NOTE (correction): send_notification() used to unconditionally
    claim "sent": True - no email/Slack/webhook/any real notification
    channel is wired up here at all, it only ever constructed the
    payload dict. An operator relying on this to know a forecast
    failure alert genuinely went out would have no real signal either
    way. Zero real callers anywhere in the codebase (verified via
    grep). Now honestly discloses that nothing was actually dispatched.
    """

    def send_notification(self, title: str, message: str) -> dict[str, Any]:
        """Construct an operational notification payload (no real dispatch channel connected)."""
        return {
            "title": title,
            "message": message,
            "sent": False,
            "status": "NOT_SENT_NO_NOTIFICATION_CHANNEL_CONNECTED",
        }
