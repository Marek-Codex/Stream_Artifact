"""
Bot Account Step for Setup Wizard
Connect separate bot account (OPTIONAL)
"""

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel


class BotStep(BaseStep):
    """Bot account setup step (optional)"""
    
    def get_title(self) -> str:
        return "🤖 Bot Account Setup (Optional)"
    
    def show(self):
        """Show the bot setup step"""
        self.update_title(self.get_title())
        
        # Implementation here...
        placeholder_label = StandardLabel(
            self.content_frame,
            text="Bot Account Setup - Coming Soon",
            font=("Segoe UI", 16),
            text_color=self.colors['text_primary']
        )
        placeholder_label.pack(expand=True)
    
    def can_skip(self) -> bool:
        return True
    
    def skip(self):
        """Mark bot as skipped and use broadcaster account"""
        self.wizard_data['skip_bot'] = True
        self.wizard_data['use_broadcaster_as_bot'] = True
