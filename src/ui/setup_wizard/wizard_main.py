"""
Main Setup Wizard Coordinator
Manages the overall setup process and step navigation
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Optional, Callable, List
import logging
import threading

from ..components.standard_widgets import (
    StandardFrame, StandardButton, StandardLabel, StandardProgressBar
)
from .steps.welcome_step import WelcomeStep
from .steps.platform_step import PlatformStep
from .steps.broadcaster_step import BroadcasterStep
from .steps.bot_step import BotStep
from .steps.ai_step import AIStep
from .steps.apis_step import APIsStep
from .steps.backup_step import BackupStep
from .steps.complete_step import CompleteStep

logger = logging.getLogger(__name__)


class SetupWizard:
    """Main setup wizard coordinator"""

    def __init__(self, parent, app, config, colors: Dict, on_complete: Callable): # Added app
        self.parent = parent
        self.app = app # Store app instance
        self.config = config
        self.colors = colors
        self.on_complete = on_complete
        self.window: Optional[ctk.CTkToplevel] = None # Type hint for window
        
        # Wizard state
        self.current_step_index = 0 # Renamed for clarity
        self.wizard_data = self._load_initial_data() # Load data from config

        # Initialize steps, passing app to each step
        # Each step constructor will need to be updated to accept 'app'
        self.steps: List[object] = [
            WelcomeStep(self, self.app),
            PlatformStep(self, self.app),
            BroadcasterStep(self, self.app),
            BotStep(self, self.app),
            AIStep(self, self.app),
            APIsStep(self, self.app),
            BackupStep(self, self.app),
            CompleteStep(self, self.app)
        ]

        # UI components
        self.title_label: Optional[StandardLabel] = None
        self.step_label: Optional[StandardLabel] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.content_frame: Optional[StandardFrame] = None
        self.button_frame: Optional[StandardFrame] = None
        self.prev_btn: Optional[StandardButton] = None
        self.next_btn: Optional[StandardButton] = None
        self.skip_btn: Optional[StandardButton] = None

        logger.info("🧙 Setup Wizard initialized with loaded/default data.")

    def _load_initial_data(self) -> Dict:
        """Load initial data from config or use defaults."""
        defaults = {
            'platform': 'twitch', # Default platform
            'broadcaster_connected': False, # This state should be derived, not stored directly
            'broadcaster_token': '',
            'broadcaster_username': '',
            'bot_connected': False, # Similar to broadcaster_connected
            'bot_token': '',
            'bot_username': '',
            'use_broadcaster_as_bot': True,
            'ai_configured': False, # Should be derived based on if key exists and is valid
            'openrouter_key': '',
            'ai_selected_model': self.config.get('ai', 'default_model', 'meta-llama/llama-3.2-3b-instruct:free'), # Example
            'ai_free_models_only': True,
            'elevenlabs_key': '',
            'rawg_key': '',
            'backup_configured': False, # Derived
            'backup_type': 'local',
            'github_token': '',
            # Skip flags are transient for the wizard session, not usually stored in config
            'skip_bot': False,
            'skip_ai': False,
            'skip_apis': False,
            'skip_backup': False
        }
        
        loaded_data = {
            'platform': self.config.get('twitch', 'platform', defaults['platform']),
            'broadcaster_token': self.config.get('twitch', 'broadcaster_token', defaults['broadcaster_token']),
            'broadcaster_username': self.config.get('twitch', 'broadcaster_username', defaults['broadcaster_username']),
            'bot_token': self.config.get('twitch', 'bot_token', defaults['bot_token']),
            'bot_username': self.config.get('twitch', 'bot_username', defaults['bot_username']),
            'use_broadcaster_as_bot': self.config.get_bool('twitch', 'use_broadcaster_as_bot', defaults['use_broadcaster_as_bot']),
            'openrouter_key': self.config.get('ai', 'openrouter_api_key', defaults['openrouter_key']),
            'ai_selected_model': self.config.get('ai', 'selected_model', defaults['ai_selected_model']),
            'ai_free_models_only': self.config.get_bool('ai', 'free_models_only', defaults['ai_free_models_only']),
            'elevenlabs_key': self.config.get('ai', 'elevenlabs_api_key', defaults['elevenlabs_key']),
            'rawg_key': self.config.get('ai', 'rawg_api_key', defaults['rawg_key']),
            'backup_type': self.config.get('backup', 'type', defaults['backup_type']),
            'github_token': self.config.get('backup', 'github_token', defaults['github_token']),
        }
        
        # Derive dynamic states
        loaded_data['broadcaster_connected'] = bool(loaded_data['broadcaster_token'] and loaded_data['broadcaster_username'])
        loaded_data['bot_connected'] = bool(loaded_data['bot_token'] and loaded_data['bot_username'])
        loaded_data['ai_configured'] = bool(loaded_data['openrouter_key']) # Basic check, real validation in step
        loaded_data['backup_configured'] = bool(loaded_data['github_token'] and loaded_data['backup_type'] == 'github')

        # Merge with defaults for any missing keys (like skip flags)
        final_data = {**defaults, **loaded_data}
        logger.debug(f"Wizard initial data: {final_data}")
        return final_data

    def show(self):
        """Show the setup wizard."""
        try:
            if self.window is None or not self.window.winfo_exists(): # Ensure window is recreated if closed
                self._create_window()
            else: # If window exists, just bring to front
                self.window.deiconify()
                self.window.lift()
                self.window.focus_force()
            
        except Exception as e:
            logger.error(f"❌ Setup wizard show error: {e}", exc_info=True) # Add exc_info

    def lift_and_focus(self):
        """Brings an existing wizard window to the front and focuses it."""
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
        else:
            self.show() # If not existing, create and show

    def _create_window(self):
        """Create the wizard window."""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Stream Artifact - Setup Wizard")
        # Use a slightly smaller default, or make it configurable
        self.window.geometry(self.config.get('ui', 'wizard_geometry', "900x650"))
        self.window.configure(fg_color=self.colors['bg_primary'])
        
        self.window.transient(self.parent) # Make modal relative to parent
        self.window.grab_set() # Grab event focus
        
        self.window.after(20, self._center_window) # Slightly longer delay for better centering
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._create_layout()
        self._show_current_step() # Renamed

    def _create_layout(self):
        """Create the main wizard layout."""
        # Header: Title, Step Indicator, Progress Bar
        header_frame = StandardFrame(self.window, height=100, fg_color=self.colors['bg_secondary'], border_width=0) # Reduced height
        header_frame.pack(fill="x", padx=10, pady=(10,5))
        header_frame.pack_propagate(False)

        self.title_label = StandardLabel(header_frame, text="🧙 SETUP WIZARD", font=("Segoe UI", 20, "bold"), text_color=self.colors['accent_primary']) # Smaller font
        self.title_label.pack(pady=(5,2))

        self.step_label = StandardLabel(header_frame, text="Step 1 of X", font=("Segoe UI", 11), text_color=self.colors['text_secondary']) # Smaller font
        self.step_label.pack(pady=(0,5))

        self.progress_bar = ctk.CTkProgressBar(header_frame, height=15, progress_color=self.colors['accent_primary'], fg_color=self.colors['bg_tertiary']) # Slimmer
        self.progress_bar.pack(fill="x", padx=20, pady=(0,10))
        self.progress_bar.set(0)

        # Content Frame: Where step content is displayed
        self.content_frame = StandardFrame(self.window, fg_color=self.colors['bg_secondary'], border_color=self.colors['border_color'], border_width=1)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Button Frame: Navigation buttons
        self.button_frame = StandardFrame(self.window, height=70, fg_color=self.colors['bg_secondary'], border_width=0) # Reduced height
        self.button_frame.pack(fill="x", padx=10, pady=(5,10))
        self.button_frame.pack_propagate(False)
        
        # Centralize buttons in their own frame for better spacing control
        nav_buttons_container = StandardFrame(self.button_frame, fg_color="transparent")
        nav_buttons_container.pack(expand=True)


        self.prev_btn = StandardButton(nav_buttons_container, text="◀ Previous", command=self._previous_step, width=110, height=35) # Adjusted size
        self.prev_btn.pack(side="left", padx=10, pady=10)

        self.skip_btn = StandardButton(nav_buttons_container, text="Skip Step", command=self._skip_current_step, width=100, height=35, fg_color=self.colors.get('warning_color', 'orange')) # Adjusted size
        self.skip_btn.pack(side="left", padx=10, pady=10)

        self.next_btn = StandardButton(nav_buttons_container, text="Next ▶", command=self._next_or_finish_step, width=110, height=35) # Adjusted size
        self.next_btn.pack(side="right", padx=10, pady=10)

    def _center_window(self):
        """Center the wizard window on the parent or screen."""
        self.window.update_idletasks() # Ensure dimensions are calculated
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        # Ensure it's not off-screen if parent is minimized or very small
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))

        self.window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def _show_current_step(self):
        """Displays the content for the current step and updates UI elements."""
        if 0 <= self.current_step_index < len(self.steps):
            current_step_obj = self.steps[self.current_step_index]
            
            self.step_label.configure(text=f"Step {self.current_step_index + 1} of {len(self.steps)}: {current_step_obj.get_title()}")
            progress_value = (self.current_step_index + 1) / len(self.steps)
            self.progress_bar.set(progress_value)
            
            for widget in self.content_frame.winfo_children(): # Clear previous step's content
                widget.destroy()
            
            current_step_obj.show() # Ask the step to render its content
            
            self.prev_btn.configure(state="normal" if self.current_step_index > 0 else "disabled")
            self.next_btn.configure(text="Finish" if self.current_step_index == len(self.steps) - 1 else "Next ▶")
            
            if hasattr(current_step_obj, 'can_skip') and current_step_obj.can_skip():
                self.skip_btn.pack(side="left", padx=10, pady=10) # Ensure it's visible
            else:
                self.skip_btn.pack_forget() # Hide if not skippable
        else:
            logger.error(f"Invalid step index: {self.current_step_index}")


    def _previous_step(self):
        """Navigates to the previous step."""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()

    def _next_or_finish_step(self):
        """Validates current step and navigates to the next, or finishes setup."""
        current_step_obj = self.steps[self.current_step_index]
        
        if hasattr(current_step_obj, 'validate') and not current_step_obj.validate():
            logger.warning(f"Validation failed for step: {current_step_obj.get_title()}")
            # Step itself should show error message via messagebox or inline
            return
        
        # Call save_data if the step has it, to update self.wizard_data
        if hasattr(current_step_obj, 'save_data'):
            current_step_obj.save_data()

        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self._show_current_step()
        else:
            self._finish_setup() # All steps done, finalize

    def _skip_current_step(self):
        """Skips the current step if skippable."""
        current_step_obj = self.steps[self.current_step_index]
        if hasattr(current_step_obj, 'can_skip') and current_step_obj.can_skip():
            if hasattr(current_step_obj, 'skip'):
                current_step_obj.skip() # Allow step to perform custom skip logic
            logger.info(f"Skipped step: {current_step_obj.get_title()}")
            self._next_or_finish_step() # Proceed as if validated
        else:
            logger.warning(f"Attempted to skip non-skippable step: {current_step_obj.get_title()}")


    def _finish_setup(self):
        """Finalizes the setup process."""
        try:
            # Apply configuration from wizard data
            self._apply_configuration()
            
            # Save configuration
            self.config.save()
            
            # Mark setup as complete
            self.config.set('app', 'setup_complete', True)
            self.config.save()
            
            # Close window
            self.window.destroy()
            
            # Call completion callback
            if self.on_complete:
                self.on_complete()
            
            logger.info("✅ Setup wizard completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Setup wizard failed: {e}")
            messagebox.showerror("Setup Error", f"Failed to complete setup: {str(e)}")
    
    def _apply_configuration(self):
        """Apply wizard data to configuration"""
        # Twitch configuration
        if self.wizard_data.get('broadcaster_token'):
            self.config.set('twitch', 'broadcaster_token', self.wizard_data['broadcaster_token'])
            self.config.set('twitch', 'broadcaster_username', self.wizard_data['broadcaster_username'])
        
        if self.wizard_data.get('bot_token'):
            self.config.set('twitch', 'bot_token', self.wizard_data['bot_token'])
            self.config.set('twitch', 'bot_username', self.wizard_data['bot_username'])
        
        self.config.set('twitch', 'use_broadcaster_as_bot', self.wizard_data.get('use_broadcaster_as_bot', True))
        
        # AI Services
        if self.wizard_data.get('openrouter_key'):
            self.config.set('ai', 'openrouter_api_key', self.wizard_data['openrouter_key'])
        
        if self.wizard_data.get('elevenlabs_key'):
            self.config.set('ai', 'elevenlabs_api_key', self.wizard_data['elevenlabs_key'])
        
        if self.wizard_data.get('rawg_key'):
            self.config.set('ai', 'rawg_api_key', self.wizard_data['rawg_key'])
        
        # Cloud backup
        if self.wizard_data.get('github_token'):
            self.config.set('backup', 'github_token', self.wizard_data['github_token'])
        
        self.config.set('backup', 'backup_type', self.wizard_data.get('backup_type', 'local'))
    
    def _on_closing(self):
        """Handle window closing"""
        result = messagebox.askyesno(
            "Close Setup",
            "Are you sure you want to close the setup wizard?\\n"
            "You can run it again later from the main menu."
        )
        
        if result:
            self.window.destroy()
