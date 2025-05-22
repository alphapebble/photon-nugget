"""
Audit module for Project Intelligence.

This module provides functionality for recording and querying audit trails
of actions taken in the system.
"""

from project_intelligence.audit.audit_trail import (
    AuditRecord,
    AuditTrailManager,
    default_audit_manager,
)

__all__ = [
    "AuditRecord",
    "AuditTrailManager",
    "default_audit_manager",
]