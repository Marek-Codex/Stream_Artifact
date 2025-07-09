"""
Additional APIs Step for Setup Wizard
Configure additional APIs like ElevenLabs, RAWG (OPTIONAL)
"""

import webbrowser
from tkinter import messagebox
from typing import TYPE_CHECKING, Dict # Added Dict

from .base_step import BaseStep
from ...components.standard_widgets import (
    StandardFrame, StandardLabel, StandardButton, StandardEntry
)

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class APIsStep(BaseStep):
    """Additional APIs configuration step (optional)"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        self.api_entries: Dict[str, StandardEntry] = {} # To store entry widgets
        self.status_label: StandardLabel = None # For overall status
        # self.app can be used for API validation if implemented in the future

    def get_title(self) -> str:
        return "🔌 Additional APIs (Optional)"
    
    def show(self):
        """Show the additional APIs step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display
        
        apis_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        apis_frame.pack(fill="both", expand=True, padx=20, pady=15) # Adjusted padding
        
        # Friendly intro
        intro_label = StandardLabel(
            apis_frame,
            text="🔌 Want to add even more features?\n"
                 "These APIs are completely optional and can enhance your stream experience!",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center",
            wraplength=apis_frame.winfo_width() - 40 if apis_frame.winfo_width() > 50 else 500
        )
        intro_label.pack(pady=(0,15)) # Adjusted padding
        
        # --- ElevenLabs Section ---
        self._create_api_section_ui( # Renamed helper
            apis_frame,
            title="🎙️ ElevenLabs (Text-to-Speech)",
            description="Add AI voice generation to your stream!\n"
                        "💰 Pricing: Free tier available (10,000 characters/month)\n"
                        "🎯 Great for: TTS donations, AI voice responses, sound effects",
            data_key="elevenlabs_key", # Key for wizard_data
            api_name_for_ui="ElevenLabs", # User-friendly name for UI elements
            signup_url="https://elevenlabs.io/app/speech-synthesis",
            obscure_key=True
        )
        
        # --- RAWG Section ---
        self._create_api_section_ui( # Renamed helper
            apis_frame,
            title="🎮 RAWG (Game Database)",
            description="Get game information, reviews, and metadata!\n"
                        "💰 Pricing: Completely FREE (no credit card required)\n"
                        "🎯 Great for: !game commands, stream overlays, game info",
            data_key="rawg_key", # Key for wizard_data
            api_name_for_ui="RAWG", # User-friendly name for UI elements
            signup_url="https://rawg.io/apidocs",
            obscure_key=False # RAWG keys are often not sensitive
        )
        
        # Overall Status Display
        self.status_label = StandardLabel(
            apis_frame,
            text="❌ No additional APIs configured", # Default text
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors.get('text_secondary', '#9d9d9d') # Default color
        )
        self.status_label.pack(pady=15) # Adjusted padding
        
        self._update_overall_status_display() # Set initial status text
    
    def _create_api_section_ui(self, parent_frame, title: str, description: str, data_key: str, api_name_for_ui: str, signup_url: str, obscure_key: bool = True):
        """Helper to create a UI section for a single API service."""
        section_frame = StandardFrame(
            parent_frame,
            fg_color=self.colors.get('bg_tertiary', '#2a2a2a'),
            border_color=self.colors.get('accent_secondary', self.colors.get('border_color', '#404040')), # Use accent or default border
            border_width=1,
            corner_radius=5
        )
        section_frame.pack(fill="x", pady=10) # Consistent padding
        
        title_label = StandardLabel(
            section_frame, text=title, font=("Segoe UI", 14, "bold"),
            text_color=self.colors.get('accent_primary', '#3CA0FF')
        )
        title_label.pack(pady=(10,5))
        
        desc_label = StandardLabel(
            section_frame, text=description, font=("Segoe UI", 11),
            text_color=self.colors.get('text_secondary', '#d4d4d4'), justify="left",
            wraplength=section_frame.winfo_width() - 40 if section_frame.winfo_width() > 50 else 350
        )
        desc_label.pack(pady=(0,10), padx=20, fill="x")

        controls_frame = StandardFrame(section_frame, fg_color="transparent") # Transparent inner frame
        controls_frame.pack(fill="x", padx=20, pady=(0,10))

        get_key_btn_text = f"🔗 Get {api_name_for_ui} API Key"
        if "free" in description.lower() and "rawg" in api_name_for_ui.lower() : # Special case for RAWG free
             get_key_btn_text = f"🔑 Get {api_name_for_ui} API Key (Free)"

        get_btn = self.create_action_button(
            controls_frame, get_key_btn_text, lambda url=signup_url: webbrowser.open(url),
            primary=False, width=220, height=35
        )
        get_btn.pack(pady=(5,10)) # Spacing for button

        key_input_frame = StandardFrame(controls_frame, fg_color="transparent")
        key_input_frame.pack(fill="x")

        key_label_text = f"{api_name_for_ui} API Key:"
        key_label = StandardLabel(key_input_frame, text=key_label_text, font=("Segoe UI", 11))
        key_label.pack(side="left", padx=(0,5))
        
        entry = StandardEntry(
            key_input_frame, placeholder_text=f"Enter your {api_name_for_ui} key...",
            width=300, height=35, show="*" if obscure_key else None
        )
        entry.pack(side="left", expand=True, fill="x", padx=(0,10))
        self.api_entries[data_key] = entry # Store entry widget

        # Pre-fill from wizard_data
        if self.wizard_data.get(data_key):
            entry.insert(0, self.wizard_data[data_key])

        test_btn = self.create_action_button(
            key_input_frame, "🧪 Test & Save", lambda dk=data_key, e=entry: self._test_and_save_specific_api_key(dk, e),
            primary=True, width=120, height=35
        )
        test_btn.pack(side="left")
        
    def _test_and_save_specific_api_key(self, data_key: str, entry_widget: StandardEntry):
        """Test and save a specific API key."""
        key_value = entry_widget.get().strip()
        api_name = data_key.replace("_key", "").upper() # Simple way to get name like "ELEVENLABS"
        
        if not key_value:
            messagebox.showerror("API Key Missing", f"Please enter the {api_name} API key.", parent=self.wizard.window)
            return
        
        # TODO: Implement actual API validation for each service if possible.
        # This would involve making a test call to the respective API.
        # For now, we'll assume any non-empty key is "valid" for saving.
        
        self.wizard_data[data_key] = key_value
        self.wizard_data[f'{data_key.replace("_key", "")}_configured'] = True # e.g., 'elevenlabs_configured' = True
        
        self._update_overall_status_display()
        messagebox.showinfo("API Key Saved", f"{api_name} API key has been saved.", parent=self.wizard.window)

    def _update_overall_status_display(self):
        """Update the main status label based on which APIs are configured."""
        configured_apis = []
        if self.wizard_data.get('elevenlabs_configured'): # Check the specific flag
            configured_apis.append("ElevenLabs")
        if self.wizard_data.get('rawg_configured'): # Check the specific flag
            configured_apis.append("RAWG")
        # Add checks for other APIs if they are added

        if configured_apis:
            self.status_label.configure(
                text=f"✅ Configured: {', '.join(configured_apis)}",
                text_color=self.colors.get('success_color', 'green')
            )
        else:
            self.status_label.configure(
                text="❌ No additional APIs configured yet.",
                text_color=self.colors.get('text_secondary', '#9d9d9d')
            )

    def save_data(self):
        """Data is saved when individual 'Test & Save' buttons are clicked."""
        # Ensure all entries are re-saved in case user edited without pressing Test & Save again
        for data_key, entry_widget in self.api_entries.items():
            if entry_widget and entry_widget.winfo_exists():
                 current_val = entry_widget.get().strip()
                 self.wizard_data[data_key] = current_val
                 # Update configured status based on if key is present
                 self.wizard_data[f'{data_key.replace("_key","")}_configured'] = bool(current_val)
        self._update_overall_status_display() # Refresh status based on final values

    def can_skip(self) -> bool:
        return True # This step is entirely optional.
    
    def skip(self):
        """Handle skipping this step: ensure all related API keys are cleared."""
        self.wizard_data['skip_apis'] = True
        # Explicitly clear the API keys this step manages
        self.wizard_data['elevenlabs_key'] = ''
        self.wizard_data['elevenlabs_configured'] = False
        self.wizard_data['rawg_key'] = ''
        self.wizard_data['rawg_configured'] = False
        # Add clearing for any other APIs managed by this step
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.info("Additional APIs step skipped. All related API keys cleared.")
