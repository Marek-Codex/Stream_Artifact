"""
Platform Selection Step for Setup Wizard
Choose streaming platform (currently only Twitch)
"""

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel


class PlatformStep(BaseStep):
    """Platform selection step"""
    
    def get_title(self) -> str:
        return "🎮 Choose Your Streaming Platform"
    
    def show(self):
        """Show the platform selection step"""
        self.update_title(self.get_title())
        
        platform_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        platform_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Question
        question_label = StandardLabel(
            platform_frame,
            text="Which platform will you be streaming on?",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors['accent_primary']
        )
        question_label.pack(pady=20)
        
        # Platform options
        options_frame = StandardFrame(
            platform_frame,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        options_frame.pack(fill="x", pady=20)
        
        # Twitch (primary option)
        self.create_action_button(
            options_frame,
            "🟣 TWITCH",
            lambda: self._select_platform("twitch"),
            primary=True
        )
        
        # Current selection
        if self.wizard_data.get('platform'):
            selection_label = StandardLabel(
                platform_frame,
                text=f"✅ Selected: {self.wizard_data['platform'].title()}",
                font=("Segoe UI", 12, "bold"),
                text_color=self.colors['success_color']
            )
            selection_label.pack(pady=10)
        
        # Coming soon
        self.create_info_section(
            platform_frame,
            "COMING SOON",
            [
                "📺 YouTube Live integration",
                "⚡ Kick.com support", 
                "🎬 Other streaming platforms"
            ],
            "🔜"
        )
    
    def _select_platform(self, platform: str):
        """Select streaming platform"""
        self.wizard_data['platform'] = platform
        self.wizard.logger.info(f"📺 Platform selected: {platform}")
        self.show()  # Refresh to show selection
    
    def validate(self) -> bool:
        """Validate platform selection"""
        if not self.wizard_data.get('platform'):
            from tkinter import messagebox
            messagebox.showwarning("Platform Required", "Please select a streaming platform.")
            return False
        return True
    
    def can_skip(self) -> bool:
        return False  # Cannot skip platform selection
