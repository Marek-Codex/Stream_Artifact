"""
Base Step Class for Setup Wizard
Provides common functionality for all wizard steps
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, TYPE_CHECKING # Added List, Callable, TYPE_CHECKING
import logging
import customtkinter as ctk # Added ctk for type hinting if needed

from ...components.standard_widgets import (
    StandardFrame, StandardButton, StandardLabel
)

# For type hinting to avoid circular import
if TYPE_CHECKING:
    from ..wizard_main import SetupWizard # Assuming wizard_main.py contains SetupWizard
    from ....core.app import StreamArtifact # Corrected relative import path assumption

logger = logging.getLogger(__name__)


class BaseStep(ABC):
    """Base class for all wizard steps"""
    
    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'): # Added app argument and type hints
        self.wizard = wizard
        self.app = app # Store the app instance
        self.config = wizard.config # Convenience reference
        self.colors = wizard.colors # Convenience reference
        self.wizard_data = wizard.wizard_data # Convenience reference
        # self.content_frame is accessed via property below
        
    @abstractmethod
    def show(self):
        """
        Render the step content in the wizard's content_frame.
        This method MUST be overridden by subclasses.
        The step title should be set via self.wizard.step_label in wizard_main.py
        """
        # Example:
        # placeholder_label = StandardLabel(
        #     self.content_frame,
        #     text=f"Implement content for: {self.get_title()}",
        #     font=("Segoe UI", 14)
        # )
        # placeholder_label.pack(expand=True, padx=20, pady=20)
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        """
        Return the title for this specific step.
        This is used by the wizard to update the step indicator label.
        Example: "Welcome" or "Twitch Connection"
        """
        return "Unnamed Step"
    
    def validate(self) -> bool:
        """
        Validate data entered in this step before proceeding.
        Override in subclasses if validation is needed.
        Should show a messagebox or inline error on failure.
        """
        return True
    
    def save_data(self):
        """
        Save data from this step's widgets into self.wizard_data.
        Called by the wizard before moving to the next step (after validation).
        Override in subclasses that collect data.
        """
        pass

    def can_skip(self) -> bool:
        """Whether this step can be skipped"""
        return False
    
    def skip(self):
        """
        Handle skip action. For example, setting default values in self.wizard_data
        or marking a specific part of the configuration as skipped.
        """
        logger.info(f"Skipping step: {self.get_title()}")
        # Example: self.wizard_data[f'skipped_{self.get_title().lower().replace(" ", "_")}'] = True
        pass
    
    def create_info_section(self, parent_frame: ctk.CTkFrame, title: str, items: List[str], icon: str = "ℹ️") -> StandardFrame:
        """Create a standard info section using StandardFrame and StandardLabel."""
        info_frame = StandardFrame(
            parent_frame,
            fg_color=self.colors.get('bg_tertiary_alt', self.colors.get('bg_tertiary', '#2a2a2a')), # Use a slightly different tertiary if available
            border_color=self.colors.get('border_color', '#404040'),
            border_width=1,
            corner_radius=5
        )
        info_frame.pack(fill="x", pady=(10,15), padx=10) # Adjusted padding
        
        info_title = StandardLabel(
            info_frame,
            text=f"{icon} {title.upper()}", # Uppercase title
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors.get('accent_primary', '#3CA0FF')
        )
        info_title.pack(pady=(10,5), anchor="w", padx=15) # Anchor west
        
        for item_text in items:
            item_label = StandardLabel(
                info_frame,
                text=f"• {item_text}", # Add bullet point
                font=("Segoe UI", 11), # Slightly smaller font for items
                text_color=self.colors.get('text_secondary', '#d4d4d4'),
                justify="left",
                anchor="w",
                 # Attempt to calculate wraplength; requires parent_frame to be sized.
                 # This might be tricky if parent_frame's size isn't determined yet.
                 # wraplength=parent_frame.winfo_width() - 50 if parent_frame.winfo_width() > 50 else 300
            )
            # Pack with fill='x' to allow text wrapping if wraplength is effective
            item_label.pack(pady=2, anchor="w", padx=20, fill="x", expand=True)
        
        return info_frame
    
    def create_action_button(self, parent_frame: ctk.CTkFrame, text: str, command: Callable, primary: bool = True, width: int = 250, height: int = 40) -> StandardButton:
        """Create a standard action button using StandardButton."""
        if primary:
            fg_color = self.colors.get('accent_primary', '#3CA0FF')
            # Text color for primary button should contrast with its bg
            text_color = self.colors.get('text_inverse_on_accent', self.colors.get('bg_primary', '#000000'))
            hover_color = self.colors.get('accent_primary_hover', '#5fb3ff')
        else:
            fg_color = self.colors.get('bg_tertiary', '#2a2a2a')
            text_color = self.colors.get('text_primary', '#ffffff')
            hover_color = self.colors.get('hover_color', self.colors.get('bg_quaternary', '#3a3a3a'))

        button = StandardButton(
            parent_frame,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=fg_color,
            text_color=text_color,
            hover_color=hover_color # Add hover_color
        )
        button.pack(pady=10)
        return button
    
    def update_wizard_main_title(self, title: str): # Renamed for clarity
        """
        Updates the main title label of the wizard (the "SETUP WIZARD" part).
        Typically not needed as the main title is static.
        The step-specific title is handled by wizard_main.py using get_title().
        """
        if self.wizard.title_label: # Check if wizard's main title label exists
            self.wizard.title_label.configure(text=title)
    
    @property
    def content_frame(self) -> ctk.CTkFrame: # Added type hint
        """Get the content frame from the wizard to draw step UI into."""
        if self.wizard and hasattr(self.wizard, 'content_frame'):
            return self.wizard.content_frame
        else:
            # This case should ideally not happen if wizard is structured correctly
            logger.error("Wizard or content_frame not available in BaseStep.")
            # Fallback or raise error, e.g., create a dummy frame or raise Exception
            # For now, returning None and callers should handle it, but this indicates a problem.
            # return None # Or raise an exception
            # Creating a dummy frame to prevent crashes, but this is a sign of misuse
            class DummyFrame(ctk.CTkFrame): pass
            logger.warning("Returning a DUMMY frame for content_frame in BaseStep. This is an issue.")
            return DummyFrame(None) # This will likely cause visual issues or further errors
