"""Unit test suite for hpc_workflow/workflow_notifications.py (ACF-HPC-104)."""

from acf.hpc_workflow.workflow_notifications import WorkflowNotifications


def test_send_notification_honestly_discloses_no_real_channel_connected():
    """
    CORRECTED: send_notification() used to unconditionally claim
    "sent": True - no email/Slack/webhook/any real notification channel
    is wired up here at all, it only ever constructed the payload dict.
    An operator relying on this to know a forecast failure alert
    genuinely went out would have no real signal either way.
    """
    notifications = WorkflowNotifications()
    result = notifications.send_notification("AROME run failed", "Job wf_arome_00utc failed at stage MODEL_RUN")
    assert result["title"] == "AROME run failed"
    assert result["message"] == "Job wf_arome_00utc failed at stage MODEL_RUN"
    assert result["sent"] is False
    assert result["status"] == "NOT_SENT_NO_NOTIFICATION_CHANNEL_CONNECTED"
