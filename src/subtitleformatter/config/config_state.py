"""
Configuration State Management for SubtitleFormatter.

Manages working configuration, saved configuration, and snapshots for restore functionality.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import copy


class ConfigState:
    """Manages configuration state with working, saved, and snapshot configurations."""
    
    def __init__(self):
        self.working_config: Dict[str, Any] = {}  # Current working configuration
        self.saved_config: Dict[str, Any] = {}    # Saved configuration
        self.snapshot_config: Dict[str, Any] = {} # Snapshot for restore functionality
        self.is_dirty: bool = False               # Whether there are unsaved changes
        self.last_saved_path: Optional[str] = None # Path to last saved configuration
        self.snapshot_path: Optional[str] = None   # Path captured when snapshot was created
    
    def load_from_saved(self, config: Dict[str, Any], config_path: Optional[str] = None):
        """Load configuration from saved state."""
        self.saved_config = copy.deepcopy(config)
        self.working_config = copy.deepcopy(config)
        self.snapshot_config = copy.deepcopy(config)
        self.is_dirty = False
        self.last_saved_path = config_path
    
    def update_working_config(self, config: Dict[str, Any]):
        """Update working configuration."""
        self.working_config = copy.deepcopy(config)
        self.is_dirty = True
    
    def save_working_config(self, config_path: Optional[str] = None):
        """Save working configuration."""
        self.saved_config = copy.deepcopy(self.working_config)
        self.is_dirty = False
        if config_path:
            self.last_saved_path = config_path
    
    def restore_from_snapshot(self):
        """Restore configuration from snapshot."""
        self.working_config = copy.deepcopy(self.snapshot_config)
        self.saved_config = copy.deepcopy(self.snapshot_config)
        self.is_dirty = False
        # Also restore the last_saved_path to snapshot_path if available
        if self.snapshot_path is not None:
            self.last_saved_path = self.snapshot_path
    
    def create_snapshot(self):
        """Create a snapshot of current saved configuration."""
        self.snapshot_config = copy.deepcopy(self.saved_config)
        # Capture the path of the saved configuration at snapshot time
        self.snapshot_path = self.last_saved_path
    
    def get_working_config(self) -> Dict[str, Any]:
        """Get current working configuration."""
        return copy.deepcopy(self.working_config)
    
    def get_saved_config(self) -> Dict[str, Any]:
        """Get saved configuration."""
        return copy.deepcopy(self.saved_config)
    
    def get_snapshot_config(self) -> Dict[str, Any]:
        """Get snapshot configuration."""
        return copy.deepcopy(self.snapshot_config)
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.is_dirty
    
    def reset(self):
        """Reset all configurations."""
        self.working_config.clear()
        self.saved_config.clear()
        self.snapshot_config.clear()
        self.is_dirty = False
        self.last_saved_path = None
        self.snapshot_path = None
