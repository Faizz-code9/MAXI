
import logging
import re
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    ),
)

from app import audit_logger


def test_audit_log_timestamp_is_iso8601(caplog):
    """Verify the timestamp format of an emitted audit log."""
    with caplog.at_level(logging.INFO, logger="minimax.audit"):
        audit_logger.info("US-12 timestamp verification")

    assert caplog.records, "No audit log record was captured"

    record = caplog.records[-1]
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    actual_log_line = formatter.format(record)
    timestamp = actual_log_line.split(" [", 1)[0]

    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:,\d{3})?",
        timestamp,
    ), f"Timestamp is not ISO 8601: {timestamp}"
