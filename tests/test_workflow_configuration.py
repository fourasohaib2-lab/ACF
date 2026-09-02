"""
Tests for acf.hpc_workflow.workflow_configuration.WorkflowConfiguration
- found with zero test coverage during a repo-wide scan for silently-
swallowed exceptions (a real config file that existed but failed to
parse used to be silently replaced by the same default as a genuinely
missing file, with no logging either way).
"""

from __future__ import annotations

import logging

from acf.hpc_workflow.workflow_configuration import WorkflowConfiguration

LOGGER_NAME = "acf.hpc_workflow.workflow_configuration"


def test_missing_file_returns_the_honest_default_silently(tmp_path, caplog):
    config = WorkflowConfiguration(config_dir=str(tmp_path))
    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        result = config.load_config("does_not_exist.yaml")

    assert result == {"mode": "operational", "auto_restart": True}
    assert caplog.records == []  # a genuinely missing file is the honest default case - no warning


def test_valid_config_file_is_returned_as_is(tmp_path):
    (tmp_path / "workflow.yaml").write_text("mode: test\nauto_restart: false\nextra: 1\n", encoding="utf-8")
    config = WorkflowConfiguration(config_dir=str(tmp_path))

    result = config.load_config("workflow.yaml")

    assert result == {"mode": "test", "auto_restart": False, "extra": 1}


def test_malformed_yaml_logs_a_real_warning_and_falls_back_to_the_default(tmp_path, caplog):
    (tmp_path / "workflow.yaml").write_text("mode: [unterminated\n", encoding="utf-8")
    config = WorkflowConfiguration(config_dir=str(tmp_path))

    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        result = config.load_config("workflow.yaml")

    assert result == {"mode": "operational", "auto_restart": True}
    assert len(caplog.records) == 1
    assert "workflow.yaml" in caplog.records[0].message


def test_non_mapping_yaml_logs_a_real_warning_and_falls_back_to_the_default(tmp_path, caplog):
    (tmp_path / "workflow.yaml").write_text("- item1\n- item2\n", encoding="utf-8")
    config = WorkflowConfiguration(config_dir=str(tmp_path))

    with caplog.at_level(logging.WARNING, logger=LOGGER_NAME):
        result = config.load_config("workflow.yaml")

    assert result == {"mode": "operational", "auto_restart": True}
    assert len(caplog.records) == 1
    assert "list" in caplog.records[0].message
