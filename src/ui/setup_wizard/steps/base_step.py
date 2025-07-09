"""
Base Step Class for Setup Wizard
Provides common functionality for all wizard steps
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

from ...components.standard_widgets import (
    StandardFrame, StandardButton, StandardLabel
)

logger = logging.getLogger(__name__)


class BaseStep(ABC):
    """Base class for all wizard steps"""
    
    def __init__(self, wizard):
        self.wizard = wizard
        self.config = wizard.config
        self.colors = wizard.colors
        self.wizard_data = wizard.wizard_data
        # content_frame will be set when the wizard window is created
        
    @abstractmethod
    def show(self):
        """Show the step content"""
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        """Get the step title"""
        pass
    
    def validate(self) -> bool:
        """Validate step data before proceeding"""
        return True
    
    def can_skip(self) -> bool:
        """Whether this step can be skipped"""
        return False
    
    def skip(self):
        """Handle skip action"""
        pass
    
    def create_info_section(self, parent, title: str, items: list, icon: str = "ℹ️"):
        """Create a standard info section"""
        info_frame = StandardFrame(
            parent,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        info_frame.pack(fill="x", pady=20)
        
        info_title = StandardLabel(
            info_frame,
            text=f"{icon} {title}",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['accent_primary']
        )
        info_title.pack(pady=10)
        
        for item in items:
            item_label = StandardLabel(
                info_frame,
                text=item,
                font=("Segoe UI", 10),
                text_color=self.colors['text_secondary']
            )
            item_label.pack(pady=2, anchor="w", padx=20)
        
        return info_frame
    
    def create_action_button(self, parent, text: str, command, primary: bool = True):
        """Create a standard action button"""
        color = self.colors['accent_primary'] if primary else self.colors['bg_tertiary']
        text_color = self.colors['bg_primary'] if primary else self.colors['text_primary']
        
        button = StandardButton(
            parent,
            text=text,
            command=command,
            width=250,
            height=50,
            fg_color=color,
            text_color=text_color
        )
        button.pack(pady=10)
        return button
    
    def update_title(self, title: str):
        """Update the wizard title"""
        self.wizard.title_label.configure(text=title)
    
    @property
    def content_frame(self):
        """Get the content frame from the wizard"""
        return self.wizard.content_frame
