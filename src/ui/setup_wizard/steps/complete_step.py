"""
Completion Step for Setup Wizard
Show setup summary and finish
"""
from typing import TYPE_CHECKING

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel # StandardButton via helper

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class CompleteStep(BaseStep):
    """Setup completion step"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # No app-specific logic usually needed here.

    def get_title(self) -> str:
        return "🎉 Setup Complete!" # Step-specific part of the title
    
    def show(self):
        """Show the completion step content, summarizing the setup."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display
        
        complete_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        complete_frame.pack(fill="both", expand=True, padx=30, pady=20) # Adjusted padding
        
        # Success Message
        success_header_label = StandardLabel(
            complete_frame,
            text="Your Stream Artifact bot is ready to go!",
            font=("Segoe UI", 18, "bold"), # Consistent font style
            text_color=self.colors.get('success_color', 'green'),
            justify="center"
        )
        success_header_label.pack(pady=(10,15))
        
        # Configuration Summary Section
        summary_items = self._build_summary_list() # Get list of summary strings
        if summary_items:
            self.create_info_section( # Helper from BaseStep
                complete_frame,
                "Configuration Summary", # Title for info section
                summary_items, # List of strings
                "📋" # Icon
            )
        
        # Next Steps Information
        self.create_info_section(
            complete_frame,
            "What's Next?",
            [
                "Click 'Finish' to save these settings and launch the main interface.",
                "If services are configured, the bot may attempt to connect automatically.",
                "Explore the different panels to manage commands, timers, AI, etc.",
                "Customize further options in the main Settings panel."
            ],
            "🚀" # Icon
        )
    
    def _build_summary_list(self) -> list[str]:
        """Helper to construct the list of summary strings based on wizard_data."""
        items = []

        # Broadcaster Account
        bc_user = self.wizard_data.get('broadcaster_username', 'N/A')
        bc_status = "Connected" if self.wizard_data.get('broadcaster_connected') else "NOT CONNECTED (Required!)"
        items.append(f"🎬 Broadcaster: {bc_user} ({bc_status})")

        # Bot Account
        if self.wizard_data.get('use_broadcaster_as_bot', True):
            items.append("🤖 Bot Account: Using broadcaster account")
        else:
            bot_user = self.wizard_data.get('bot_username', 'N/A')
            bot_status = "Connected" if self.wizard_data.get('bot_connected') else "Separate Bot NOT Connected"
            items.append(f"🤖 Bot Account: {bot_user} ({bot_status})")

        # AI Services (OpenRouter)
        ai_key_present = bool(self.wizard_data.get('openrouter_key'))
        ai_model = self.wizard_data.get('ai_selected_model', 'None Selected').split(':')[0] # Cleaner name
        if self.wizard_data.get('skip_ai'):
            items.append("🔮 AI (OpenRouter): Skipped")
        elif ai_key_present and ai_model != 'None Selected':
            items.append(f"🔮 AI (OpenRouter): Configured (Model: {ai_model})")
        elif ai_key_present:
            items.append("🔮 AI (OpenRouter): Key set, model selection pending")
        else:
            items.append("🔮 AI (OpenRouter): Not configured")

        # Other APIs (Example: ElevenLabs, RAWG - checking specific configured flags)
        if self.wizard_data.get('elevenlabs_configured'):
            items.append("🗣️ ElevenLabs TTS: Configured")
        elif not self.wizard_data.get('skip_apis', False) and not self.wizard_data.get('elevenlabs_key'):
             items.append("🗣️ ElevenLabs TTS: Not configured")


        if self.wizard_data.get('rawg_configured'):
            items.append("🎮 RAWG Games DB: Configured")
        elif not self.wizard_data.get('skip_apis', False) and not self.wizard_data.get('rawg_key'):
            items.append("🎮 RAWG Games DB: Not configured")

        if self.wizard_data.get('skip_apis') and not self.wizard_data.get('elevenlabs_configured') and not self.wizard_data.get('rawg_configured'):
            items.append("🔌 Other APIs: Skipped")


        # Backup Configuration
        backup_type = self.wizard_data.get('backup_type', 'local').title()
        backup_status_detail = ""
        if backup_type.lower() == 'github gist': # Check normalized value
            gh_token_present = bool(self.wizard_data.get('github_token'))
            backup_status_detail = "(Token Present)" if gh_token_present else "(Token NOT Set - Configure in Settings)"
        items.append(f"☁️ Backup: {backup_type} {backup_status_detail}".strip())

        return items

    def can_skip(self) -> bool:
        return False  # The completion step itself cannot be skipped.

    def validate(self) -> bool:
        # No validation needed on the completion step itself.
        return True

    def save_data(self):
        # All data should have been saved by individual steps.
        pass
