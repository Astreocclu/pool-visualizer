"""
Pool Visualizer - Prompts
-------------------------
DEPRECATED: This file exists for backwards compatibility.
Use tenant-specific prompts instead:
  - api/tenants/pools/prompts.py
  - api/tenants/windows/prompts.py
  - api/tenants/roofs/prompts.py
"""


def get_cleanup_prompt():
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_cleanup_prompt()


def get_screen_insertion_prompt(feature_type: str, options: dict):
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_screen_insertion_prompt(feature_type, options)


def get_quality_check_prompt(scope: dict = None):
    """Redirect to pools tenant."""
    from api.tenants.pools import prompts
    return prompts.get_quality_check_prompt(scope)
