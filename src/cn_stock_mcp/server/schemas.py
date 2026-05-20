"""Backward-compatible re-export facade.

All schema classes and types are now defined in ``cn_stock_mcp.server.schema_defs``.
This module re-exports them so that existing ``from cn_stock_mcp.server.schemas import X`` continues to work.
"""

from cn_stock_mcp.server.schema_defs import *  # noqa: F401,F403
from cn_stock_mcp.server.schema_defs import __all__  # noqa: F401
