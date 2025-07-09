"""
Welcome Step for Setup Wizard
Initial welcome and introduction screen
"""

import webbrowser
import os

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel, StandardButton


class WelcomeStep(BaseStep):
    """Welcome step for the setup wizard"""
    
    def get_title(self) -> str:
        return "🎉 Welcome to Stream Artifact!"
    
    def show(self):
        """Show the welcome step"""
        self.update_title(self.get_title())
        
        # Main welcome content
        welcome_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        welcome_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Welcome description
        desc_label = StandardLabel(
            welcome_frame,
            text="Welcome to Stream Artifact - your professional AI chatbot companion!\\n\\n"
                 "This setup wizard will guide you through connecting your accounts\\n"
                 "and configuring your bot. Most steps are optional.",
            font=("Segoe UI", 14),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # Features section
        self.create_info_section(
            welcome_frame,
            "KEY FEATURES",
            [
                "🤖 AI-powered chat responses with multiple models",
                "🎮 Advanced Twitch integration and moderation",
                "📊 Real-time analytics and viewer insights", 
                "🎨 Professional, customizable interface",
                "☁️ Optional cloud backup and sync",
                "🔐 Secure OAuth authentication"
            ],
            "✨"
        )
        
        # Requirements section
        self.create_info_section(
            welcome_frame,
            "SETUP REQUIREMENTS",
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
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_orange'],
            border_width=2
        )
        disclaimer_frame.pack(fill="x", pady=20)
        
        disclaimer_title = StandardLabel(
            disclaimer_frame,
            text="💡 About Costs & Free Features",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['accent_orange']
        )
        disclaimer_title.pack(pady=10)
        
        disclaimer_text = StandardLabel(
            disclaimer_frame,
            text="Stream Artifact is completely free to use! 🎉\n\n"
                 "• The bot itself costs nothing and has no subscription fees\n"
                 "• Most features work without any API keys or external services\n"
                 "• AI features are optional and default to free models only\n"
                 "• We'll clearly explain any costs before you enable paid features\n"
                 "• You're always in control of what you spend (if anything!)",
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        disclaimer_text.pack(pady=10, padx=20)
        
        # Help button for API key guide
        help_btn = StandardButton(
            disclaimer_frame,
            text="📖 API Key Setup Guide",
            command=self._open_api_guide,
            width=200,
            height=35,
            fg_color=self.colors['accent_orange'],
            hover_color=self.colors['hover_color']
        )
        help_btn.pack(pady=10)
        
        # Instructions
        instr_label = StandardLabel(
            welcome_frame,
            text="Click 'Next' to begin the setup process.",
            font=("Segoe UI", 12),
            text_color=self.colors['text_secondary'],
            justify="center"
        )
        instr_label.pack(pady=20)
    
    def _open_api_guide(self):
        """Open the API key setup guide"""
        guide_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "docs", "API_KEY_SETUP.md")
        
        if os.path.exists(guide_path):
            # Open with default markdown viewer or text editor
            os.startfile(guide_path)
        else:
            # Fallback: open GitHub documentation
            webbrowser.open("https://github.com/your-repo/Stream_Artifact/blob/main/docs/API_KEY_SETUP.md")
    
    def can_skip(self) -> bool:
        return False  # Cannot skip welcome step
