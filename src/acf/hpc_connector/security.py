"""HPC Security & Authentication Manager (ACF-HPC-001)."""

import os
import re

from acf.hpc_connector.logging import log_hpc_event

# RFC 1123 hostname / dotted-IPv4 shape (permissive - format only, not a
# live DNS/reachability check).
_HOSTNAME_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9\-.]*[A-Za-z0-9])?$")
# POSIX portable username character set (IEEE Std 1003.1-2017 §3.437).
_USERNAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]*\$?$")


class HPCSecurityManager:
    """Manages SSH authentication, key paths, and host key verification."""

    def __init__(self, ssh_key_path: str | None = None) -> None:
        self.ssh_key_path = os.path.expanduser(ssh_key_path or "~/.ssh/id_rsa")

    def has_valid_ssh_key(self) -> bool:
        """Check if SSH key file exists and is accessible."""
        return os.path.exists(self.ssh_key_path)

    def validate_connection(self, host: str, user: str) -> bool:
        """Validate SSH connection parameter FORMAT (hostname/username shape) without exposing credentials.

        NOTE (correction): used to unconditionally return True for any
        host/user, including empty strings or values containing shell
        metacharacters - not a genuine validation despite the name and
        docstring. This checks format only (RFC 1123 hostname/IPv4
        shape, POSIX username charset) - it does NOT verify the host is
        reachable, the user exists, or that authentication would
        actually succeed (no live connection is attempted here, exactly
        as originally documented). Currently unused by
        HPCConnectionManager (verified via grep - self.security is
        constructed but validate_connection() is never called), so this
        closes a real but previously-inert gap rather than changing
        any existing behavior.
        """
        is_valid = bool(host) and bool(user) and bool(_HOSTNAME_RE.match(host)) and bool(_USERNAME_RE.match(user))
        log_hpc_event(
            "INFO" if is_valid else "WARNING",
            f"Validating SSH parameter format for {user!r}@{host!r}: {'valid' if is_valid else 'INVALID'}",
        )
        return is_valid
