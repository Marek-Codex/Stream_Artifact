"""
Welcome Step for Setup Wizard
Initial welcome and introduction screen
"""

import webbrowser
import os
from typing import TYPE_CHECKING # For type hinting

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel, StandardButton

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class WelcomeStep(BaseStep):
    """Welcome step for the setup wizard"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # No app-specific logic needed for WelcomeStep, but good practice.

    def get_title(self) -> str:
        return "🎉 Welcome to Stream Artifact!" # This is the step-specific part of the title
    
    def show(self):
        """Show the welcome step content."""
        # The main wizard now sets the full step title string, so no need to call self.update_title() here.
        
        welcome_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        welcome_frame.pack(fill="both", expand=True, padx=40, pady=20) # Reduced pady
        
        # Welcome description
        desc_label = StandardLabel(
            welcome_frame,
            text="Welcome to Stream Artifact - your professional AI chatbot companion!\n\n"
                 "This setup wizard will guide you through connecting your accounts\n"
                 "and configuring your bot. Most steps are optional.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center"
        )
        desc_label.pack(pady=(10,15)) # Adjusted padding
        
        # Features section
        self.create_info_section( # Helper from BaseStep
            welcome_frame,
            "Key Features", # Title for the info section
            [
                "🤖 AI-powered chat responses with multiple models",
                "🎮 Advanced Twitch integration and moderation",
                "📊 Real-time analytics and viewer insights", 
                "🎨 Professional, customizable interface",
                "☁️ Optional cloud backup and sync",
                "🔐 Secure OAuth authentication"
            ],
            "✨" # Icon for the info section
        )
        
        # Requirements section
        self.create_info_section(
            welcome_frame,
            "Setup Requirements",
            [
                "✅ Required: Twitch broadcaster account (your main streaming account)",
                "🔧 Optional: Separate bot account (recommended for cleaner chat)",
                "🤖 Optional: AI service API keys (OpenRouter, ElevenLabs, etc.)",
                "☁️ Optional: Cloud backup service (GitHub)"
            ],
            "📋"
        )
        
        # Friendly disclaimer about costs
        disclaimer_frame = StandardFrame(
            welcome_frame,
            fg_color=self.colors.get('bg_tertiary', '#2a2a2a'),
            border_color=self.colors.get('accent_orange', '#fbbf24'),
            border_width=2,
            corner_radius=5
        )
        disclaimer_frame.pack(fill="x", pady=15) # Adjusted padding
        
        disclaimer_title = StandardLabel(
            disclaimer_frame,
            text="💡 About Costs & Free Features",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors.get('accent_orange', '#fbbf24')
        )
        disclaimer_title.pack(pady=(10,5))
        
        disclaimer_text = StandardLabel(
            disclaimer_frame,
            text="Stream Artifact is completely free to use! 🎉\n\n"
                 "• The bot itself costs nothing and has no subscription fees.\n"
                 "• Most features work without any API keys or external services.\n"
                 "• AI features are optional and default to free models only.\n"
                 "• We'll clearly explain any costs before you enable paid features.\n"
                 "• You're always in control of what you spend (if anything!)",
            font=("Segoe UI", 11),
            text_color=self.colors.get('text_secondary', '#d4d4d4'),
            justify="left"
        )
        disclaimer_text.pack(pady=(0,10), padx=20)
        
        # Help button for API key guide
        help_btn = StandardButton(
            disclaimer_frame,
            text="📖 API Key Setup Guide",
            command=self._open_api_guide,
            width=200, # Keep width consistent if defined in create_action_button
            height=35, # Keep height consistent
            fg_color=self.colors.get('accent_orange', '#fbbf24'),
            # Use a hover color that makes sense for an orange button
            hover_color=self.colors.get('accent_orange_hover', self.colors.get('hover_color', '#3a3a3a')),
            text_color=self.colors.get('text_inverse_on_accent', self.colors.get('bg_primary', '#000000'))
        )
        help_btn.pack(pady=(0,10))
        
        # Instructions
        instr_label = StandardLabel(
            welcome_frame,
            text="Click 'Next' to begin the setup process.",
            font=("Segoe UI", 12),
            text_color=self.colors.get('text_secondary', '#d4d4d4'),
            justify="center"
        )
        instr_label.pack(pady=15) # Adjusted padding
    
    def _open_api_guide(self):
        """Open the API key setup guide, trying local file first, then web."""
        try:
            # Construct path relative to the current project structure more reliably
            # Assuming this file is src/ui/setup_wizard/steps/welcome_step.py
            # Project root is four levels up from 'steps' directory
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            guide_path = project_root / "docs" / "API_KEY_SETUP.md"

            if guide_path.exists():
                # For cross-platform opening, webbrowser.open with file:// URI is often better
                webbrowser.open(guide_path.as_uri())
                self.wizard.app.main_window.log_activity(f"Opened local API guide: {guide_path.as_uri()}") # Example log
            else:
                # Fallback: open GitHub documentation (replace with actual URL)
                # Placeholder URL, update this to the correct one for your repository
                github_guide_url = "https://github.com/Marek-Codex/stream-artifact/blob/main/docs/API_KEY_SETUP.md"
                webbrowser.open(github_guide_url)
                self.wizard.app.main_window.log_activity(f"Opened web API guide: {github_guide_url}")
        except Exception as e:
            self.wizard.app.main_window.log_activity(f"Error opening API guide: {e}") # Log error
            webbrowser.open("https://github.com/Marek-Codex/stream-artifact/tree/main/docs") # Fallback to docs dir


    def can_skip(self) -> bool:
        return False  # Welcome step should not be skippable
