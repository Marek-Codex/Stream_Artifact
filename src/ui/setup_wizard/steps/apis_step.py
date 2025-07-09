"""
Additional APIs Step for Setup Wizard
Configure additional APIs like ElevenLabs, RAWG (OPTIONAL)
"""

import webbrowser
from tkinter import messagebox

from .base_step import BaseStep
from ...components.standard_widgets import (
    StandardFrame, StandardLabel, StandardButton, StandardEntry
)


class APIsStep(BaseStep):
    """Additional APIs configuration step (optional)"""
    
    def get_title(self) -> str:
        return "🔌 Additional APIs (Optional)"
    
    def show(self):
        """Show the additional APIs step"""
        self.update_title(self.get_title())
        
        apis_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        apis_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Friendly intro
        intro_label = StandardLabel(
            apis_frame,
            text="🔌 Want to add even more features?\n"
                 "These APIs are completely optional and can enhance your stream experience!",
            font=("Segoe UI", 14),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        intro_label.pack(pady=20)
        
        # ElevenLabs Section
        elevenlabs_section = self._create_api_section(
            apis_frame,
            "🎙️ ElevenLabs (Text-to-Speech)",
            "Add AI voice generation to your stream!\n"
            "💰 Pricing: Free tier available (10,000 characters/month)\n"
            "🎯 Great for: TTS donations, AI voice responses, sound effects",
            "elevenlabs",
            "https://elevenlabs.io/app/speech-synthesis"
        )
        
        # RAWG Section  
        rawg_section = self._create_api_section(
            apis_frame,
            "🎮 RAWG (Game Database)",
            "Get game information, reviews, and metadata!\n"
            "💰 Pricing: Completely FREE (no credit card required)\n"
            "🎯 Great for: !game commands, stream overlays, game info",
            "rawg",
            "https://rawg.io/apidocs"
        )
        
        # Status
        self.status_label = StandardLabel(
            apis_frame,
            text="❌ No additional APIs configured",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['text_secondary']
        )
        self.status_label.pack(pady=20)
        
        # Update status if any APIs are configured
        self._update_status()
    
    def _create_api_section(self, parent, title, description, api_key, signup_url):
        """Create a section for an API service"""
        section = StandardFrame(
            parent,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_secondary'],
            border_width=1
        )
        section.pack(fill="x", pady=15)
        
        # Title
        title_label = StandardLabel(
            section,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['accent_primary']
        )
        title_label.pack(pady=10)
        
        # Description
        desc_label = StandardLabel(
            section,
            text=description,
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        desc_label.pack(pady=5, padx=20)
        
        # Controls frame
        controls_frame = StandardFrame(
            section,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        controls_frame.pack(fill="x", padx=20, pady=15)
        
        # Get API key button
        get_btn = StandardButton(
            controls_frame,
            text=f"� Get {api_key.upper()} API Key" if api_key != "rawg" else "🔑 Get RAWG API Key (Free)",
            command=lambda: webbrowser.open(signup_url),
            width=220,
            height=35,
            fg_color=self.colors['accent_secondary']
        )
        get_btn.pack(pady=10)
        
        # API Key input
        key_label = StandardLabel(
            controls_frame,
            text=f"{api_key.upper()} API Key:",
            font=("Segoe UI", 11),
            text_color=self.colors['text_primary']
        )
        key_label.pack(pady=(10, 5))
        
        entry = StandardEntry(
            controls_frame,
            placeholder_text=f"Enter your {api_key} API key...",
            width=350,
            height=35,
            show="*" if api_key != "rawg" else None  # RAWG keys don't need to be hidden
        )
        entry.pack(pady=5)
        
        # Test button
        test_btn = StandardButton(
            controls_frame,
            text="🧪 Test & Save",
            command=lambda: self._test_api_key(api_key, entry),
            width=120,
            height=35,
            fg_color=self.colors['success_color']
        )
        test_btn.pack(pady=10)
        
        return section
    
    def _test_api_key(self, api_type, entry):
        """Test and save an API key"""
        key = entry.get().strip()
        
        if not key:
            messagebox.showerror("Error", f"Please enter your {api_type.upper()} API key first.")
            return
        
        # TODO: Implement actual API validation
        # For now, just store it
        self.wizard_data[f'{api_type}_key'] = key
        self.wizard_data[f'{api_type}_configured'] = True
        
        self._update_status()
        
        messagebox.showinfo(
            "Success!",
            f"✅ {api_type.upper()} API key saved successfully!\n\n"
            f"You can now use {api_type}-powered features in your stream."
        )
    
    def _update_status(self):
        """Update the status label based on configured APIs"""
        configured = []
        
        if self.wizard_data.get('elevenlabs_configured'):
            configured.append("ElevenLabs")
        if self.wizard_data.get('rawg_configured'):
            configured.append("RAWG")
        
        if configured:
            self.status_label.configure(
                text=f"✅ Configured: {', '.join(configured)}",
                text_color=self.colors['success_color']
            )
        else:
            self.status_label.configure(
                text="❌ No additional APIs configured",
                text_color=self.colors['text_secondary']
            )
    
    def can_skip(self) -> bool:
        return True
    
    def skip(self):
        """Mark APIs as skipped"""
        self.wizard_data['skip_apis'] = True
