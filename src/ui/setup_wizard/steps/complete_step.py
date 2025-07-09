"""
Completion Step for Setup Wizard
Show setup summary and finish
"""

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel


class CompleteStep(BaseStep):
    """Setup completion step"""
    
    def get_title(self) -> str:
        return "🎉 Setup Complete!"
    
    def show(self):
        """Show the completion step"""
        self.update_title(self.get_title())
        
        complete_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        complete_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Success message
        success_label = StandardLabel(
            complete_frame,
            text="Your Stream Artifact bot is ready to go!",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors['success_color'],
            justify="center"
        )
        success_label.pack(pady=20)
        
        # Configuration summary
        summary_items = []
        if self.wizard_data.get('broadcaster_connected'):
            summary_items.append(f"🎬 Broadcaster: {self.wizard_data.get('broadcaster_username', 'Connected')}")
        
        if self.wizard_data.get('bot_connected'):
            summary_items.append(f"🤖 Bot Account: {self.wizard_data.get('bot_username', 'Connected')}")
        elif self.wizard_data.get('use_broadcaster_as_bot'):
            summary_items.append("🤖 Bot: Using broadcaster account")
        
        if self.wizard_data.get('openrouter_key'):
            summary_items.append("🤖 OpenRouter AI: Configured")
        
        if self.wizard_data.get('elevenlabs_key'):
            summary_items.append("🗣️ ElevenLabs TTS: Configured")
        
        if self.wizard_data.get('rawg_key'):
            summary_items.append("🎮 RAWG Games: Configured")
        
        if self.wizard_data.get('backup_configured'):
            summary_items.append(f"☁️ Backup: {self.wizard_data.get('backup_type', 'local').title()}")
        
        if summary_items:
            self.create_info_section(
                complete_frame,
                "CONFIGURATION SUMMARY",
                summary_items,
                "📋"
            )
        
        # Next steps
        self.create_info_section(
            complete_frame,
            "WHAT'S NEXT",
            [
                "• Click 'Finish' to launch the main interface",
                "• Your bot will automatically connect to chat",
                "• Test AI responses with commands like !ai",
                "• Customize settings in the Settings panel",
                "• Monitor chat activity in real-time"
            ],
            "🚀"
        )
    
    def can_skip(self) -> bool:
        return False  # Cannot skip completion
