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
    
    def __init__(self, parent, config, colors: Dict, on_complete: Callable):
        self.parent = parent
        self.config = config
        self.colors = colors
        self.on_complete = on_complete
        self.window = None
        
        # Wizard state
        self.current_step = 0
        self.wizard_data = {
            'platform': 'twitch',
            'broadcaster_connected': False,
            'broadcaster_token': '',
            'broadcaster_username': '',
            'bot_connected': False,
            'bot_token': '',
            'bot_username': '',
            'use_broadcaster_as_bot': True,
            'ai_configured': False,
            'openrouter_key': '',
            'elevenlabs_key': '',
            'rawg_key': '',
            'backup_configured': False,
            'backup_type': 'local',
            'github_token': '',
            'skip_bot': False,
            'skip_ai': False,
            'skip_apis': False,
            'skip_backup': False
        }
        
        # Initialize steps
        self.steps: List[object] = [
            WelcomeStep(self),
            PlatformStep(self),
            BroadcasterStep(self),
            BotStep(self),
            AIStep(self),
            APIsStep(self),
            BackupStep(self),
            CompleteStep(self)
        ]
        
        # UI components
        self.title_label = None
        self.step_label = None
        self.progress_bar = None
        self.content_frame = None
        self.button_frame = None
        self.prev_btn = None
        self.next_btn = None
        self.skip_btn = None
        
        logger.info("🧙 Setup Wizard initialized")
    
    def show(self):
        """Show the setup wizard"""
        try:
            if self.window is None:
                self._create_window()
            
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            
        except Exception as e:
            logger.error(f"❌ Setup wizard show error: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_window(self):
        """Create the wizard window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Stream Artifact - Setup Wizard")
        self.window.geometry("1000x700")
        self.window.configure(fg_color=self.colors['bg_primary'])
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.after(10, self._center_window)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Create main layout
        self._create_layout()
        
        # Show first step
        self._show_step()
    
    def _create_layout(self):
        """Create the main wizard layout"""
        # Header frame
        header_frame = StandardFrame(
            self.window,
            height=120,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['accent_primary'],
            border_width=2
        )
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Title
        self.title_label = StandardLabel(
            header_frame,
            text="🧙 SETUP WIZARD",
            font=("Segoe UI", 24, "bold"),
            text_color=self.colors['accent_primary']
        )
        self.title_label.pack(pady=10)
        
        # Step indicator
        self.step_label = StandardLabel(
            header_frame,
            text="Step 1 of 8",
            font=("Segoe UI", 12),
            text_color=self.colors['text_secondary']
        )
        self.step_label.pack()
        
        # Progress bar
        progress_frame = StandardFrame(
            header_frame,
            height=30,
            fg_color=self.colors['bg_tertiary']
        )
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            progress_color=self.colors['accent_primary'],
            fg_color=self.colors['bg_primary']
        )
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        # Content frame
        self.content_frame = StandardFrame(
            self.window,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button frame
        self.button_frame = StandardFrame(
            self.window,
            height=80,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        self.button_frame.pack(fill="x", padx=10, pady=10)
        self.button_frame.pack_propagate(False)
        
        # Navigation buttons
        self.prev_btn = StandardButton(
            self.button_frame,
            text="◀ Previous",
            command=self._prev_step,
            width=120,
            height=40,
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary']
        )
        self.prev_btn.pack(side="left", padx=20, pady=20)
        
        self.skip_btn = StandardButton(
            self.button_frame,
            text="Skip",
            command=self._skip_step,
            width=100,
            height=40,
            fg_color=self.colors['warning_color'],
            text_color=self.colors['bg_primary']
        )
        self.skip_btn.pack(side="left", padx=10, pady=20)
        
        self.next_btn = StandardButton(
            self.button_frame,
            text="Next ▶",
            command=self._next_step,
            width=120,
            height=40,
            fg_color=self.colors['accent_primary'],
            text_color=self.colors['bg_primary']
        )
        self.next_btn.pack(side="right", padx=20, pady=20)
    
    def _center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _show_step(self):
        """Show the current step"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            
            # Update header
            self.step_label.configure(text=f"Step {self.current_step + 1} of {len(self.steps)}")
            
            # Update progress
            progress = (self.current_step + 1) / len(self.steps)
            self.progress_bar.set(progress)
            
            # Clear content frame
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Show step content
            step.show()
            
            # Update button states
            self.prev_btn.configure(state="disabled" if self.current_step == 0 else "normal")
            self.next_btn.configure(text="Finish" if self.current_step == len(self.steps) - 1 else "Next ▶")
            
            # Update skip button visibility
            if hasattr(step, 'can_skip') and step.can_skip():
                self.skip_btn.pack(side="left", padx=10, pady=20)
            else:
                self.skip_btn.pack_forget()
    
    def _prev_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_step()
    
    def _next_step(self):
        """Go to next step"""
        current_step = self.steps[self.current_step]
        
        # Validate current step
        if hasattr(current_step, 'validate') and not current_step.validate():
            return  # Stay on current step if validation fails
        
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._show_step()
        else:
            self._finish_setup()
    
    def _skip_step(self):
        """Skip current step"""
        current_step = self.steps[self.current_step]
        
        # Let the step handle its own skip logic
        if hasattr(current_step, 'skip'):
            current_step.skip()
        
        self._next_step()
    
    def _finish_setup(self):
        """Finish setup and apply configuration"""
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
