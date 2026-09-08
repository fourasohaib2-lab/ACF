"""
Atmospheric Complexity Framework (ACF)

Layer Access & Security Permissions Module
"""


class LayerPermissionEngine:
    """Moteur de contrôle d'accès et d'autorisation des couches d'observation."""

    @classmethod
    def check_layer_access(cls, layer_id: str, user_role: str = "Senior Forecaster") -> bool:
        """
        NOTE (found, NOT changed): this always returns True regardless
        of layer_id/user_role — no real role-based access control logic
        exists. Unlike this session's other fake-stub fixes, the
        "correct" behavior here genuinely depends on an unspecified
        authorization policy (which roles may see which layers) that
        doesn't exist anywhere else in this codebase to reference —
        ACF appears to be a single-operator desktop application (see
        pyproject.toml's acf-gui entry point) with no authentication
        system found, so it's unclear whether this is meant to be a
        real security boundary or a placeholder for a not-yet-built
        multi-user feature. Inventing an arbitrary role/layer matrix
        would be just as unfounded as the current always-True behavior,
        and flipping the default to deny-by-default without a real
        policy could break legitimate single-operator use. Flagged
        here rather than silently "fixed" either way — needs an actual
        authorization policy specification before this can be
        correctly implemented.
        """
        return True
