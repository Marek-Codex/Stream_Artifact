"""
Platform Selection Step for Setup Wizard
Choose streaming platform (currently only Twitch)
"""
from typing import TYPE_CHECKING

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel # StandardButton is used via helper

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class PlatformStep(BaseStep):
    """Platform selection step"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # App instance might be used in the future if platform selection involves API calls
        # or dynamic loading of platform-specific modules.
    
    def get_title(self) -> str:
        return "🎮 Choose Your Streaming Platform"
    
    def show(self):
        """Show the platform selection step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display

        platform_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        platform_frame.pack(fill="both", expand=True, padx=40, pady=20) # Reduced pady
        
        # Question
        question_label = StandardLabel(
            platform_frame,
            text="Which platform will you be streaming on?",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors.get('accent_primary', '#3CA0FF')
        )
        question_label.pack(pady=20)
        
        # Platform options
        options_frame = StandardFrame(
            platform_frame,
            fg_color=self.colors.get('bg_tertiary', '#2a2a2a'),
            border_color=self.colors.get('border_color', '#404040'),
            border_width=1,
            corner_radius=5
        )
        options_frame.pack(fill="x", pady=15, padx=20) # Added padx
        
        # Twitch (primary option)
        self.create_action_button( # Helper from BaseStep
            options_frame,
            "🟣 TWITCH",
            lambda: self._select_platform("twitch"),
            primary=True, # Make it look like the main choice
            width=200, height=45 # Slightly larger button
        )
        
        # Current selection display
        # This part is dynamic and will update when _select_platform calls self.show()
        current_platform = self.wizard_data.get('platform')
        if current_platform:
            selection_label = StandardLabel(
                platform_frame,
                text=f"✅ Selected: {current_platform.title()}",
                font=("Segoe UI", 12, "bold"),
                text_color=self.colors.get('success_color', 'green') # Use a success color
            )
            selection_label.pack(pady=(10, 5))
        
        # Coming soon section
        self.create_info_section( # Helper from BaseStep
            platform_frame,
            "Coming Soon", # Title for info section
            [
                "📺 YouTube Live integration",
                "⚡ Kick.com support", 
                "🎬 Other streaming platforms"
            ],
            "🔜" # Icon
        )
    
    def _select_platform(self, platform: str):
        """Handles platform selection and updates UI."""
        self.wizard_data['platform'] = platform
        # Log using the main wizard's logger if available, or app's logger
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.info(f"📺 Platform selected: {platform}")

        # Refresh the current step's view to show the selection
        # This involves clearing and re-rendering the content_frame for this step
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.show()
    
    def save_data(self):
        """
        Data is saved directly in _select_platform via self.wizard_data.
        No explicit save action needed here unless there were entry fields.
        """
        pass

    def validate(self) -> bool:
        """Validate that a platform has been selected."""
        if not self.wizard_data.get('platform'):
            from tkinter import messagebox # Local import for UI element
            messagebox.showwarning("Platform Required", "Please select a streaming platform.", parent=self.wizard.window)
            return False
        return True
    
    def can_skip(self) -> bool:
        return False  # Platform selection is fundamental and should not be skippable.
