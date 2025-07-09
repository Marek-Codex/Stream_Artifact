"""
Bot Account Step for Setup Wizard
Connect separate bot account (OPTIONAL)
"""
from typing import TYPE_CHECKING

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel # Assuming these are used when implemented

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class BotStep(BaseStep):
    """Bot account setup step (optional)"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # When implemented, self.app could be used for OAuth for the bot account.
    
    def get_title(self) -> str:
        return "🤖 Bot Account Setup (Optional)"
    
    def show(self):
        """Show the bot setup step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display

        # Current implementation is a placeholder.
        # When fully implemented, this will contain UI for:
        # 1. A switch to use broadcaster account vs. separate bot account.
        # 2. If separate bot: button to connect via OAuth, status display.
        
        placeholder_label = StandardLabel(
            self.content_frame, # Property from BaseStep
            text="Bot Account Setup - Under Construction\n(Using Broadcaster Account as Bot by Default)",
            font=("Segoe UI", 16),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center"
        )
        placeholder_label.pack(expand=True, padx=20, pady=20)

        # Default to using broadcaster as bot if this step is shown but not fully interactive yet.
        if 'use_broadcaster_as_bot' not in self.wizard_data: # Set default if not already set
            self.wizard_data['use_broadcaster_as_bot'] = True
    
    def save_data(self):
        """Save chosen bot configuration."""
        # This will be implemented when the UI elements (like the switch) are added.
        # For now, it might just ensure the default is set if nothing else was done.
        if 'use_broadcaster_as_bot' not in self.wizard_data:
             self.wizard_data['use_broadcaster_as_bot'] = True
        # logger.debug(f"Bot step save_data: use_broadcaster_as_bot = {self.wizard_data['use_broadcaster_as_bot']}")


    def can_skip(self) -> bool:
        return True # This step is optional.
    
    def skip(self):
        """Mark bot as skipped and default to using broadcaster account."""
        self.wizard_data['skip_bot'] = True
        self.wizard_data['use_broadcaster_as_bot'] = True
        # Clear any potential partial bot connection data
        self.wizard_data['bot_connected'] = False
        self.wizard_data['bot_username'] = ''
        self.wizard_data['bot_token'] = ''
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.info("Bot account step skipped. Defaulting to use broadcaster as bot.")
