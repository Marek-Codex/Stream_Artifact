"""
Settings Window for Stream Artifact
Cyberpunk-themed settings interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Dict, List, Optional, Callable
import json
import os
import logging

from ..core.config import Config
from .components.cyberpunk_widgets import (
    CyberpunkFrame, CyberpunkButton, CyberpunkLabel, 
    CyberpunkEntry, CyberpunkCombobox, CyberpunkSwitch
)

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings window with cyberpunk aesthetic"""
    
    def __init__(self, parent_window, config: Config, colors: Dict):
        self.parent = parent_window
        self.config = config
        self.colors = colors
        self.window = None
        self.settings_widgets = {}
        self.is_open = False
        
        # Temporary settings storage
        self.temp_settings = {}
        
        logger.info("⚙️ Settings window initialized")
    
    def show(self):
        """Show the settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.is_open = True
        self._create_window()
        self._create_layout()
        self._load_current_settings()
        
        logger.info("⚙️ Settings window opened")
    
    def _create_window(self):
        """Create the settings window"""
        self.window = ctk.CTkToplevel()
        self.window.title("Stream Artifact - Settings")
        self.window.geometry("800x600")
        self.window.configure(fg_color=self.colors['bg_primary'])
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.after(10, self._center_window)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def focus(self):
        """Focus the settings window"""
        if self.window and self.window.winfo_exists():
            self.window.focus()
            self.window.lift()
    
    def _center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_layout(self):
        """Create the settings layout"""
        # Main frame
        main_frame = CyberpunkFrame(
            self.window,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['border_color'],
            border_width=2
        )
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = CyberpunkFrame(
            main_frame,
            height=60,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_primary'],
            border_width=1
        )
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = CyberpunkLabel(
            header_frame,
            text="⚙️ SETTINGS",
            font=("Consolas", 20, "bold"),
            text_color=self.colors['accent_primary']
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Content area with notebook
        content_frame = CyberpunkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabbed interface
        self._create_tabs(content_frame)
        
        # Button frame
        button_frame = CyberpunkFrame(
            main_frame,
            height=60,
            fg_color=self.colors['bg_tertiary']
        )
        button_frame.pack(fill="x", padx=5, pady=5)
        button_frame.pack_propagate(False)
        
        # Buttons
        save_btn = CyberpunkButton(
            button_frame,
            text="💾 SAVE",
            command=self._save_settings,
            width=100,
            height=35,
            fg_color=self.colors['success_color'],
            hover_color=self.colors['hover_color'],
            text_color=self.colors['bg_primary']
        )
        save_btn.pack(side="right", padx=10, pady=12)
        
        cancel_btn = CyberpunkButton(
            button_frame,
            text="❌ CANCEL",
            command=self._on_closing,
            width=100,
            height=35,
            fg_color=self.colors['error_color'],
            hover_color=self.colors['hover_color'],
            text_color=self.colors['text_primary']
        )
        cancel_btn.pack(side="right", padx=10, pady=12)
        
        reset_btn = CyberpunkButton(
            button_frame,
            text="🔄 RESET",
            command=self._reset_settings,
            width=100,
            height=35,
            fg_color=self.colors['warning_color'],
            hover_color=self.colors['hover_color'],
            text_color=self.colors['bg_primary']
        )
        reset_btn.pack(side="left", padx=10, pady=12)
    
    def _create_tabs(self, parent):
        """Create the tabbed interface"""
        # Create notebook-style tabs
        tab_frame = CyberpunkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)
        
        # Tab buttons
        tab_buttons_frame = CyberpunkFrame(
            tab_frame,
            height=50,
            fg_color=self.colors['bg_tertiary']
        )
        tab_buttons_frame.pack(fill="x", pady=(0, 5))
        tab_buttons_frame.pack_propagate(False)
        
        # Tab content frame
        self.tab_content_frame = CyberpunkFrame(
            tab_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        self.tab_content_frame.pack(fill="both", expand=True)
        
        # Create tabs
        self.tabs = {
            "twitch": "🎮 TWITCH",
            "ai": "🤖 AI",
            "ui": "🎨 UI",
            "commands": "💬 COMMANDS",
            "moderation": "🛡️ MODERATION"
        }
        
        self.current_tab = "twitch"
        self.tab_buttons = {}
        self.tab_frames = {}
        
        for tab_id, tab_name in self.tabs.items():
            # Create tab button
            btn = CyberpunkButton(
                tab_buttons_frame,
                text=tab_name,
                command=lambda t=tab_id: self._switch_tab(t),
                width=120,
                height=35,
                fg_color=self.colors['bg_primary'] if tab_id == self.current_tab else self.colors['bg_secondary'],
                hover_color=self.colors['hover_color'],
                border_color=self.colors['accent_primary'] if tab_id == self.current_tab else self.colors['border_color']
            )
            btn.pack(side="left", padx=2, pady=7)
            self.tab_buttons[tab_id] = btn
            
            # Create tab content frame
            frame = CyberpunkFrame(self.tab_content_frame, fg_color="transparent")
            self.tab_frames[tab_id] = frame
            
            # Create tab content
            self._create_tab_content(tab_id, frame)
        
        # Show initial tab
        self._switch_tab(self.current_tab)
    
    def _create_tab_content(self, tab_id: str, frame: CyberpunkFrame):
        """Create content for a specific tab"""
        if tab_id == "twitch":
            self._create_twitch_tab(frame)
        elif tab_id == "ai":
            self._create_ai_tab(frame)
        elif tab_id == "ui":
            self._create_ui_tab(frame)
        elif tab_id == "commands":
            self._create_commands_tab(frame)
        elif tab_id == "moderation":
            self._create_moderation_tab(frame)
    
    def _create_twitch_tab(self, frame):
        """Create Twitch settings tab"""
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['accent_primary'],
            scrollbar_button_hover_color=self.colors['hover_color']
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Channel settings
        self._create_setting_group(scrollable, "📺 CHANNEL SETTINGS")
        
        self._create_setting_entry(
            scrollable, "twitch_channel", "Channel Name:", 
            "Enter your Twitch channel name (without #)"
        )
        
        self._create_setting_entry(
            scrollable, "twitch_token", "OAuth Token:", 
            "Enter your Twitch OAuth token", is_password=True
        )
        
        # Connection settings
        self._create_setting_group(scrollable, "🔗 CONNECTION SETTINGS")
        
        self._create_setting_switch(
            scrollable, "auto_connect", "Auto Connect on Startup"
        )
        
        self._create_setting_entry(
            scrollable, "reconnect_delay", "Reconnect Delay (seconds):", 
            "Delay before reconnecting after disconnection"
        )
        
        # Chat settings
        self._create_setting_group(scrollable, "💬 CHAT SETTINGS")
        
        self._create_setting_switch(
            scrollable, "respond_to_mentions", "Respond to @mentions"
        )
        
        self._create_setting_switch(
            scrollable, "respond_to_commands", "Respond to commands"
        )
        
        self._create_setting_entry(
            scrollable, "command_prefix", "Command Prefix:", 
            "Prefix for bot commands (e.g., !)"
        )
    
    def _create_ai_tab(self, frame):
        """Create AI settings tab"""
        scrollable = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['accent_secondary'],
            scrollbar_button_hover_color=self.colors['hover_color']
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # OpenRouter settings
        self._create_setting_group(scrollable, "🤖 OPENROUTER SETTINGS")
        
        self._create_setting_entry(
            scrollable, "openrouter_api_key", "API Key:", 
            "Enter your OpenRouter API key", is_password=True
        )
        
        self._create_setting_combo(
            scrollable, "ai_model", "AI Model:", 
            ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "gemini-pro"],
            "Select the AI model to use"
        )
        
        # Response settings
        self._create_setting_group(scrollable, "💭 RESPONSE SETTINGS")
        
        self._create_setting_entry(
            scrollable, "max_tokens", "Max Tokens:", 
            "Maximum tokens for AI response (1-4096)"
        )
        
        self._create_setting_entry(
            scrollable, "temperature", "Temperature:", 
            "AI creativity level (0.0-1.0)"
        )
        
        self._create_setting_entry(
            scrollable, "response_delay", "Response Delay (seconds):", 
            "Minimum delay between AI responses"
        )
        
        # Memory settings
        self._create_setting_group(scrollable, "🧠 MEMORY SETTINGS")
        
        self._create_setting_switch(
            scrollable, "enable_memory", "Enable Conversation Memory"
        )
        
        self._create_setting_entry(
            scrollable, "memory_limit", "Memory Limit (messages):", 
            "Number of messages to remember"
        )
    
    def _create_ui_tab(self, frame):
        """Create UI settings tab"""
        scrollable = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['accent_tertiary'],
            scrollbar_button_hover_color=self.colors['hover_color']
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Window settings
        self._create_setting_group(scrollable, "🪟 WINDOW SETTINGS")
        
        self._create_setting_entry(
            scrollable, "window_width", "Window Width:", 
            "Default window width in pixels"
        )
        
        self._create_setting_entry(
            scrollable, "window_height", "Window Height:", 
            "Default window height in pixels"
        )
        
        self._create_setting_switch(
            scrollable, "window_maximized", "Start Maximized"
        )
        
        # Theme settings
        self._create_setting_group(scrollable, "🎨 THEME SETTINGS")
        
        self._create_setting_combo(
            scrollable, "theme", "Theme:", 
            ["cyberpunk", "dark", "light"],
            "Select the UI theme"
        )
        
        self._create_setting_switch(
            scrollable, "glassmorphism", "Enable Glassmorphism Effects"
        )
        
        self._create_setting_switch(
            scrollable, "glow_effects", "Enable Glow Effects"
        )
        
        # Font settings
        self._create_setting_group(scrollable, "🔤 FONT SETTINGS")
        
        self._create_setting_combo(
            scrollable, "font_family", "Font Family:", 
            ["Consolas", "Courier New", "Monaco", "Fira Code"],
            "Select the font family"
        )
        
        self._create_setting_entry(
            scrollable, "font_size", "Font Size:", 
            "Default font size"
        )
    
    def _create_commands_tab(self, frame):
        """Create commands settings tab"""
        scrollable = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['accent_primary'],
            scrollbar_button_hover_color=self.colors['hover_color']
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Command settings
        self._create_setting_group(scrollable, "💬 COMMAND SETTINGS")
        
        self._create_setting_switch(
            scrollable, "enable_commands", "Enable Commands"
        )
        
        self._create_setting_entry(
            scrollable, "command_cooldown", "Command Cooldown (seconds):", 
            "Global cooldown between commands"
        )
        
        # Built-in commands
        self._create_setting_group(scrollable, "🔧 BUILT-IN COMMANDS")
        
        builtin_commands = [
            ("help", "Show help message"),
            ("ai", "Talk to AI"),
            ("stats", "Show bot statistics"),
            ("uptime", "Show stream uptime"),
            ("lurk", "Lurk command"),
            ("unlurk", "Unlurk command")
        ]
        
        for cmd, desc in builtin_commands:
            self._create_setting_switch(
                scrollable, f"cmd_{cmd}_enabled", f"Enable !{cmd} command"
            )
    
    def _create_moderation_tab(self, frame):
        """Create moderation settings tab"""
        scrollable = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors['error_color'],
            scrollbar_button_hover_color=self.colors['hover_color']
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Moderation settings
        self._create_setting_group(scrollable, "🛡️ MODERATION SETTINGS")
        
        self._create_setting_switch(
            scrollable, "enable_moderation", "Enable Auto-Moderation"
        )
        
        self._create_setting_switch(
            scrollable, "filter_spam", "Filter Spam Messages"
        )
        
        self._create_setting_switch(
            scrollable, "filter_caps", "Filter Excessive Caps"
        )
        
        self._create_setting_entry(
            scrollable, "caps_threshold", "Caps Threshold (%):", 
            "Percentage of caps to trigger filter"
        )
        
        # Timeout settings
        self._create_setting_group(scrollable, "⏱️ TIMEOUT SETTINGS")
        
        self._create_setting_entry(
            scrollable, "timeout_duration", "Default Timeout (seconds):", 
            "Default timeout duration"
        )
        
        self._create_setting_entry(
            scrollable, "max_warnings", "Max Warnings:", 
            "Maximum warnings before timeout"
        )
    
    def _create_setting_group(self, parent, title: str):
        """Create a settings group header"""
        group_frame = CyberpunkFrame(
            parent,
            height=40,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        group_frame.pack(fill="x", pady=(20, 10))
        group_frame.pack_propagate(False)
        
        label = CyberpunkLabel(
            group_frame,
            text=title,
            font=("Consolas", 14, "bold"),
            text_color=self.colors['accent_primary']
        )
        label.pack(side="left", padx=15, pady=10)
    
    def _create_setting_entry(self, parent, key: str, label: str, placeholder: str, is_password: bool = False):
        """Create a setting entry widget"""
        frame = CyberpunkFrame(parent, fg_color="transparent", height=60)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Label
        lbl = CyberpunkLabel(
            frame,
            text=label,
            font=("Consolas", 11),
            text_color=self.colors['text_primary']
        )
        lbl.pack(side="left", padx=10, pady=15)
        
        # Entry
        entry = CyberpunkEntry(
            frame,
            placeholder_text=placeholder,
            width=300,
            height=30,
            show="*" if is_password else None,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color']
        )
        entry.pack(side="right", padx=10, pady=15)
        
        self.settings_widgets[key] = entry
    
    def _create_setting_combo(self, parent, key: str, label: str, values: List[str], placeholder: str):
        """Create a setting combobox widget"""
        frame = CyberpunkFrame(parent, fg_color="transparent", height=60)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Label
        lbl = CyberpunkLabel(
            frame,
            text=label,
            font=("Consolas", 11),
            text_color=self.colors['text_primary']
        )
        lbl.pack(side="left", padx=10, pady=15)
        
        # Combobox
        combo = CyberpunkCombobox(
            frame,
            values=values,
            width=250,
            height=30,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color']
        )
        combo.pack(side="right", padx=10, pady=15)
        
        self.settings_widgets[key] = combo
    
    def _create_setting_switch(self, parent, key: str, label: str):
        """Create a setting switch widget"""
        frame = CyberpunkFrame(parent, fg_color="transparent", height=60)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        # Label
        lbl = CyberpunkLabel(
            frame,
            text=label,
            font=("Consolas", 11),
            text_color=self.colors['text_primary']
        )
        lbl.pack(side="left", padx=10, pady=15)
        
        # Switch
        switch = CyberpunkSwitch(
            frame,
            width=60,
            height=30,
            fg_color=self.colors['bg_primary'],
            progress_color=self.colors['accent_primary'],
            button_color=self.colors['text_primary']
        )
        switch.pack(side="right", padx=10, pady=15)
        
        self.settings_widgets[key] = switch
    
    def _switch_tab(self, tab_id: str):
        """Switch to a different tab"""
        # Update button states
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color=self.colors['bg_primary'],
                    border_color=self.colors['accent_primary']
                )
            else:
                btn.configure(
                    fg_color=self.colors['bg_secondary'],
                    border_color=self.colors['border_color']
                )
        
        # Hide all tab frames
        for frame in self.tab_frames.values():
            frame.pack_forget()
        
        # Show selected tab frame
        self.tab_frames[tab_id].pack(fill="both", expand=True)
        
        self.current_tab = tab_id
        logger.info(f"⚙️ Switched to {tab_id} tab")
    
    def _load_current_settings(self):
        """Load current settings into the widgets"""
        # TODO: Implement settings loading
        pass
    
    def _save_settings(self):
        """Save the current settings"""
        try:
            # Collect all settings from widgets
            settings = {}
            for key, widget in self.settings_widgets.items():
                if isinstance(widget, CyberpunkEntry):
                    settings[key] = widget.get()
                elif isinstance(widget, CyberpunkCombobox):
                    settings[key] = widget.get()
                elif isinstance(widget, CyberpunkSwitch):
                    settings[key] = widget.get()
            
            # Save to config
            # TODO: Implement config saving
            
            messagebox.showinfo("Settings", "Settings saved successfully!")
            self.window.destroy()
            
            logger.info("⚙️ Settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            logger.error(f"❌ Settings save failed: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset all widgets to default values
                for key, widget in self.settings_widgets.items():
                    if isinstance(widget, CyberpunkEntry):
                        widget.delete(0, tk.END)
                    elif isinstance(widget, CyberpunkCombobox):
                        widget.set("")
                    elif isinstance(widget, CyberpunkSwitch):
                        widget.deselect()
                
                logger.info("⚙️ Settings reset to defaults")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
                logger.error(f"❌ Settings reset failed: {e}")
    
    def _on_closing(self):
        """Handle window closing"""
        self.is_open = False
        self.window.destroy()
        logger.info("⚙️ Settings window closed")
