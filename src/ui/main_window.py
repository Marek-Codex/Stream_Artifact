"""
Main Window for Stream Artifact
Professional interface with resizable sections and comprehensive options
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
from typing import Dict, List, Optional, Callable
import threading
import asyncio
from datetime import datetime
import logging
from PIL import Image, ImageTk
import os
from pathlib import Path

from ..core.config import Config
from .settings_window import SettingsWindow
from .oauth_wizard import OAuthSetupWizard

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window with Streamlabs-style interface"""
    
    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.root = None
        self.is_running = False
        
        # UI Components
        self.settings_window = None
        self.oauth_wizard = None
        self.status_bar = None
        self.connection_status = None
        
        # Content panels
        self.sidebar = None
        self.main_content = None
        self.current_panel = "console"
        
        # Connection state
        self.is_connected = False
        self.connection_thread = None
        self.first_run = self.config.is_first_run()
        
        # Initialize theme
        self._setup_theme()
        
        logger.info("🎨 Streamlabs-style window initialized")
    
    def _setup_theme(self):
        """Setup the professional theme with brand color #3CA0FF"""
        # Tonal dark theme with brand primary color
        self.colors = {
            # Background layers (darkest to lightest)
            'bg_primary': '#0a0a0a',      # Darkest background
            'bg_secondary': '#1a1a1a',    # Secondary panels
            'bg_tertiary': '#2a2a2a',     # Elevated elements
            'bg_quaternary': '#3a3a3a',   # Highest elevation
            'sidebar_bg': '#151515',      # Sidebar background
            
            # Text colors
            'text_primary': '#ffffff',    # Primary text (white)
            'text_secondary': '#d4d4d4',  # Secondary text (light gray)
            'text_muted': '#9d9d9d',      # Muted text (medium gray)
            'text_inverse': '#0a0a0a',    # Inverse text (dark on light)
            
            # Border and divider colors
            'border_color': '#404040',    # Standard borders
            'border_light': '#505050',    # Lighter borders
            'border_dark': '#303030',     # Darker borders
            
            # Brand primary color (#3CA0FF) and its variations
            'accent_primary': '#3CA0FF',  # Your brand color
            'accent_primary_hover': '#5fb3ff', # Lighter hover state
            'accent_primary_pressed': '#2690ff', # Darker pressed state
            'accent_primary_muted': '#3ca0ff33', # Semi-transparent version
            'accent_primary_bg': '#3ca0ff1a',    # Very light background tint
            
            # Secondary accent colors (complementary to brand)
            'accent_secondary': '#40E0D0',    # Turquoise (complementary)
            'accent_tertiary': '#FF6B9D',     # Pink (triadic)
            'accent_blue': '#3CA0FF',         # Your brand color (alias)
            'accent_green': '#4ade80',        # Green accent
            'accent_orange': '#fbbf24',       # Orange accent  
            'accent_red': '#f87171',          # Red accent
            
            # Functional colors
            'success_color': '#4ade80',   # Green for success
            'warning_color': '#fbbf24',   # Yellow for warnings
            'error_color': '#f87171',     # Red for errors
            'info_color': '#3CA0FF',      # Use brand color for info
            
            # Interactive elements
            'button_bg': '#3CA0FF',       # Primary button background
            'button_hover': '#5fb3ff',    # Button hover state
            'button_pressed': '#2690ff',  # Button pressed state
            'hover_color': '#2a2a2a',     # General hover background
            'active_color': '#3a3a3a',    # Active state background
            'focus_color': '#3CA0FF',     # Focus ring color
            
            # Input elements
            'input_bg': '#2a2a2a',        # Input background
            'input_border': '#404040',    # Input border
            'input_focus': '#3CA0FF',     # Input focus border
            'input_placeholder': '#6b7280', # Placeholder text
            
            # Scrollbar elements
            'scrollbar_bg': '#1a1a1a',    # Scrollbar track
            'scrollbar_thumb': '#404040', # Scrollbar thumb
            'scrollbar_hover': '#505050', # Scrollbar thumb hover
            
            # Special UI elements
            'card_bg': '#1a1a1a',         # Card backgrounds
            'modal_bg': '#0a0a0a',        # Modal backgrounds
            'overlay_bg': '#00000080',    # Overlay backgrounds
            'separator_color': '#404040', # Separator lines
            
            # Status colors with brand integration
            'online_color': '#4ade80',    # Online status
            'offline_color': '#6b7280',   # Offline status
            'away_color': '#fbbf24',      # Away status
            'busy_color': '#f87171',      # Busy status
        }
        
        # Configure CTk appearance with custom theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Override CTk colors with our brand colors
        self._apply_brand_theme()
    
    def create_window(self):
        """Create the main window"""
        self.root = ctk.CTk()
        self.root.title("Stream Artifact")
        self.root.geometry("1400x900")
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        # Set window icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "Chibi_Construct.png"
            if icon_path.exists():
                # Set the window icon properly
                self.root.iconbitmap(default=str(icon_path)) if icon_path.suffix == '.ico' else None
                
                # Also set with PhotoImage for broader compatibility
                icon = Image.open(icon_path)
                icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(True, icon_photo)
                
                # Store reference to prevent garbage collection
                self.icon_photo = icon_photo
        except Exception as e:
            logger.warning(f"Could not load icon: {e}")
        
        # Make window resizable
        self.root.minsize(1200, 800)
        
        # Create main layout
        self._create_layout()
        
        # Show setup wizard if first run
        if self.first_run:
            self.root.after(1000, self._show_setup_wizard)
        
        logger.info("🪟 Main window created")
    
    def _create_layout(self):
        """Create the main window layout"""
        # Create main container with simple layout
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create sidebar
        self._create_sidebar(main_frame)
        
        # Create main content area
        self._create_main_content(main_frame)
        
        # Create status bar
        self._create_status_bar()
    
    def _create_sidebar(self, parent):
        """Create the sidebar with navigation"""
        self.sidebar = ctk.CTkFrame(
            parent,
            width=250,
            fg_color=self.colors['sidebar_bg'],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=2, pady=2)
        self.sidebar.pack_propagate(False)
        
        # Header section
        header_frame = ctk.CTkFrame(
            self.sidebar,
            height=60,
            fg_color=self.colors['bg_secondary'],
            corner_radius=0
        )
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        # App title and icon
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(expand=True)
        
        # Load and display icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "Chibi_Construct.png"
            if icon_path.exists():
                icon = Image.open(icon_path)
                icon = icon.resize((24, 24), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon)
                
                icon_label = ctk.CTkLabel(
                    title_frame,
                    image=icon_photo,
                    text="",
                    width=24,
                    height=24
                )
                icon_label.image = icon_photo  # Keep a reference
                icon_label.pack(side="left", padx=5)
        except Exception as e:
            logger.warning(f"Could not load sidebar icon: {e}")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Stream Artifact",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(side="left", padx=5)
        
        # Connection status indicator
        self.connection_indicator = ctk.CTkLabel(
            title_frame,
            text="●",
            font=("Segoe UI", 12),
            text_color=self.colors['accent_red']
        )
        self.connection_indicator.pack(side="right", padx=5)
        
        # Navigation sections
        self._create_navigation()
        
        # Bottom section with settings
        bottom_frame = ctk.CTkFrame(
            self.sidebar,
            height=100,
            fg_color=self.colors['bg_secondary'],
            corner_radius=0
        )
        bottom_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        bottom_frame.pack_propagate(False)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            bottom_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            width=200,
            height=35,
            fg_color=self.colors['button_bg'],
            hover_color=self.colors['button_hover']
        )
        settings_btn.pack(pady=10)
        
        # Setup wizard button
        wizard_btn = ctk.CTkButton(
            bottom_frame,
            text="🧙 Setup Wizard",
            command=self._show_setup_wizard,
            width=200,
            height=35,
            fg_color=self.colors['accent_orange'],
            hover_color=self.colors['accent_orange']
        )
        wizard_btn.pack(pady=5)
    
    def _create_navigation(self):
        """Create navigation menu"""
        # Scrollable frame for navigation
        nav_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=self.colors['scrollbar_thumb'],
            scrollbar_button_hover_color=self.colors['scrollbar_bg']
        )
        nav_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Navigation items (matching Streamlabs layout)
        nav_items = [
            ("📊 Console", "console", "Main dashboard and activity"),
            ("📈 Dashboard", "dashboard", "Stream analytics and stats"),
            ("👥 Subscribers", "subscribers", "Subscriber management"),
            ("💬 Commands", "commands", "Custom chat commands"),
            ("⏰ Timers", "timers", "Automated timed messages"),
            ("💭 Quotes", "quotes", "Quote system management"),
            ("📑 Extra Quotes", "extra_quotes", "Additional quote categories"),
            ("🎁 Give Away", "giveaway", "Giveaway management"),
            ("🎵 Songrequest", "songrequest", "Song request system"),
            ("🔊 Sound Files", "sound_files", "Sound effect management"),
            ("📋 Queue", "queue", "Queue system"),
            ("🔢 Counter", "counter", "Counter management"),
            ("💰 Currency", "currency", "Virtual currency system"),
            ("👤 Users", "users", "User management"),
            ("🎮 Minigames", "minigames", "Chat minigames"),
            ("📊 Poll", "poll", "Poll system"),
            ("🎯 Betting", "betting", "Betting system"),
            ("📅 Events", "events", "Event management"),
            ("🛠️ Mod Tools", "mod_tools", "Moderation tools"),
            ("🔔 Notifications", "notifications", "Alert settings"),
            ("🔗 Discord", "discord", "Discord integration")
        ]
        
        self.nav_buttons = {}
        
        for icon_text, panel_id, description in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=icon_text,
                command=lambda pid=panel_id: self._switch_panel(pid),
                width=220,
                height=35,
                fg_color="transparent",
                hover_color=self.colors['bg_tertiary'],
                text_color=self.colors['text_secondary'],
                anchor="w",
                font=("Segoe UI", 12)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[panel_id] = btn
        
        # Set console as active by default
        self._set_active_nav_button("console")
    
    def _create_main_content(self, parent):
        """Create the main content area"""
        self.main_content = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_primary'],
            corner_radius=0
        )
        self.main_content.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        
        # Content header
        content_header = ctk.CTkFrame(
            self.main_content,
            height=50,
            fg_color=self.colors['bg_secondary'],
            corner_radius=0
        )
        content_header.pack(fill="x", padx=5, pady=5)
        content_header.pack_propagate(False)
        
        # Panel title
        self.panel_title = ctk.CTkLabel(
            content_header,
            text="Console",
            font=("Segoe UI", 18, "bold"),
            text_color=self.colors['text_primary']
        )
        self.panel_title.pack(side="left", padx=15, pady=10)
        
        # Control buttons
        control_frame = ctk.CTkFrame(content_header, fg_color="transparent")
        control_frame.pack(side="right", padx=15, pady=5)
        
        # Connect/Disconnect button
        self.connect_btn = ctk.CTkButton(
            control_frame,
            text="🔗 Connect",
            command=self._toggle_connection,
            width=120,
            height=35,
            fg_color=self.colors['accent_green'],
            hover_color=self.colors['accent_green']
        )
        self.connect_btn.pack(side="right", padx=5)
        
        # Main content area with notebook for tabs
        self.content_notebook = ttk.Notebook(self.main_content)
        self.content_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize with console panel
        self._create_console_panel()
    
    def _create_console_panel(self):
        """Create the console panel (main dashboard)"""
        console_frame = ctk.CTkFrame(
            self.content_notebook,
            fg_color=self.colors['bg_primary']
        )
        self.content_notebook.add(console_frame, text="Console")
        
        # Create vertical layout for sections
        # Top section: Chat and activity
        top_frame = ctk.CTkFrame(console_frame, fg_color=self.colors['bg_secondary'])
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bottom section: Quick actions and stats
        bottom_frame = ctk.CTkFrame(console_frame, fg_color=self.colors['bg_secondary'], height=200)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        bottom_frame.pack_propagate(False)
        
        # Chat area
        chat_frame = ctk.CTkFrame(top_frame, fg_color=self.colors['bg_tertiary'])
        chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        chat_title = ctk.CTkLabel(
            chat_frame,
            text="💬 Live Chat",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['text_primary']
        )
        chat_title.pack(anchor="w", padx=10, pady=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=15,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            font=("Consolas", 10)
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bottom section: Controls and status
        # bottom_frame is already created above
        
        # Create tabbed interface for bottom section
        bottom_notebook = ttk.Notebook(bottom_frame)
        bottom_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Activity Log tab
        activity_frame = ctk.CTkFrame(bottom_notebook, fg_color=self.colors['bg_tertiary'])
        bottom_notebook.add(activity_frame, text="Activity Log")
        
        self.activity_log = scrolledtext.ScrolledText(
            activity_frame,
            height=8,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_secondary'],
            font=("Consolas", 9)
        )
        self.activity_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bot Status tab
        status_frame = ctk.CTkFrame(bottom_notebook, fg_color=self.colors['bg_tertiary'])
        bottom_notebook.add(status_frame, text="Bot Status")
        
        self._create_bot_status_section(status_frame)
        
        # Quick Commands tab
        commands_frame = ctk.CTkFrame(bottom_notebook, fg_color=self.colors['bg_tertiary'])
        bottom_notebook.add(commands_frame, text="Quick Commands")
        
        self._create_quick_commands_section(commands_frame)
    
    def _create_bot_status_section(self, parent):
        """Create bot status section"""
        status_grid = ctk.CTkFrame(parent, fg_color="transparent")
        status_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status items
        status_items = [
            ("Connection", "❌ Disconnected", "accent_red"),
            ("Uptime", "00:00:00", "text_secondary"),
            ("Messages Sent", "0", "text_secondary"),
            ("Commands Processed", "0", "text_secondary"),
            ("AI Responses", "0", "text_secondary"),
            ("Errors", "0", "accent_red")
        ]
        
        for i, (label, value, color) in enumerate(status_items):
            row = i // 3
            col = i % 3
            
            item_frame = ctk.CTkFrame(status_grid, fg_color=self.colors['bg_primary'])
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            label_widget = ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Segoe UI", 10),
                text_color=self.colors['text_muted']
            )
            label_widget.pack(pady=2)
            
            value_widget = ctk.CTkLabel(
                item_frame,
                text=value,
                font=("Segoe UI", 12, "bold"),
                text_color=self.colors[color]
            )
            value_widget.pack(pady=2)
        
        # Configure grid weights
        for i in range(3):
            status_grid.grid_columnconfigure(i, weight=1)
    
    def _create_quick_commands_section(self, parent):
        """Create quick commands section"""
        commands_frame = ctk.CTkFrame(parent, fg_color="transparent")
        commands_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Command input
        input_frame = ctk.CTkFrame(commands_frame, fg_color=self.colors['bg_primary'])
        input_frame.pack(fill="x", pady=5)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Send Command:",
            font=("Segoe UI", 12),
            text_color=self.colors['text_primary']
        )
        input_label.pack(side="left", padx=10, pady=10)
        
        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter command...",
            width=300,
            height=35,
            fg_color=self.colors['input_bg'],
            text_color=self.colors['text_primary']
        )
        self.command_entry.pack(side="left", padx=10, pady=10)
        
        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self._send_command,
            width=80,
            height=35,
            fg_color=self.colors['button_bg'],
            hover_color=self.colors['button_hover']
        )
        send_btn.pack(side="left", padx=10, pady=10)
        
        # Quick action buttons
        actions_frame = ctk.CTkFrame(commands_frame, fg_color=self.colors['bg_primary'])
        actions_frame.pack(fill="x", pady=5)
        
        quick_actions = [
            ("🔄 Refresh", self._refresh_data),
            ("🧹 Clear Chat", self._clear_chat),
            ("📊 Stats", self._show_stats),
            ("🎯 Test AI", self._test_ai)
        ]
        
        for text, command in quick_actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                width=120,
                height=35,
                fg_color=self.colors['bg_tertiary'],
                hover_color=self.colors['button_hover']
            )
            btn.pack(side="left", padx=5, pady=10)
    
    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ctk.CTkFrame(
            self.root,
            height=25,
            fg_color=self.colors['bg_secondary'],
            corner_radius=0
        )
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=self.colors['text_secondary']
        )
        self.status_text.pack(side="left", padx=10)
        
        # Connection status
        self.connection_status = ctk.CTkLabel(
            self.status_bar,
            text="Disconnected",
            font=("Segoe UI", 10),
            text_color=self.colors['accent_red']
        )
        self.connection_status.pack(side="right", padx=10)
    
    def _switch_panel(self, panel_id):
        """Switch to a different panel"""
        self.current_panel = panel_id
        self._set_active_nav_button(panel_id)
        
        # Update panel title
        panel_titles = {
            "console": "Console",
            "dashboard": "Dashboard",
            "subscribers": "Subscribers",
            "commands": "Commands",
            "timers": "Timers",
            "quotes": "Quotes",
            "extra_quotes": "Extra Quotes",
            "giveaway": "Give Away",
            "songrequest": "Song Request",
            "sound_files": "Sound Files",
            "queue": "Queue",
            "counter": "Counter",
            "currency": "Currency",
            "users": "Users",
            "minigames": "Minigames",
            "poll": "Poll",
            "betting": "Betting",
            "events": "Events",
            "mod_tools": "Mod Tools",
            "notifications": "Notifications",
            "discord": "Discord"
        }
        
        self.panel_title.configure(text=panel_titles.get(panel_id, "Unknown"))
        
        # Clear and recreate content based on panel
        self._create_panel_content(panel_id)
    
    def _set_active_nav_button(self, panel_id):
        """Set active navigation button"""
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == panel_id:
                btn.configure(
                    fg_color=self.colors['accent_blue'],
                    text_color=self.colors['text_primary']
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.colors['text_secondary']
                )
    
    def _create_panel_content(self, panel_id):
        """Create content for specific panel"""
        # Clear current content
        for widget in self.content_notebook.winfo_children():
            widget.destroy()
        
        if panel_id == "console":
            self._create_console_panel()
        elif panel_id == "commands":
            self._create_commands_panel()
        elif panel_id == "dashboard":
            self._create_dashboard_panel()
        # Add more panels as needed
        else:
            # Placeholder for other panels
            placeholder_frame = ctk.CTkFrame(
                self.content_notebook,
                fg_color=self.colors['bg_primary']
            )
            self.content_notebook.add(placeholder_frame, text=panel_id.title())
            
            placeholder_label = ctk.CTkLabel(
                placeholder_frame,
                text=f"{panel_id.title()} panel - Coming soon!",
                font=("Segoe UI", 16),
                text_color=self.colors['text_secondary']
            )
            placeholder_label.pack(expand=True)
    
    def _create_commands_panel(self):
        """Create commands management panel"""
        commands_frame = ctk.CTkFrame(
            self.content_notebook,
            fg_color=self.colors['bg_primary']
        )
        self.content_notebook.add(commands_frame, text="Commands")
        
        # Commands will be implemented here
        label = ctk.CTkLabel(
            commands_frame,
            text="Commands Panel - Under Construction",
            font=("Segoe UI", 16),
            text_color=self.colors['text_secondary']
        )
        label.pack(expand=True)
    
    def _create_dashboard_panel(self):
        """Create dashboard panel"""
        dashboard_frame = ctk.CTkFrame(
            self.content_notebook,
            fg_color=self.colors['bg_primary']
        )
        self.content_notebook.add(dashboard_frame, text="Dashboard")
        
        # Dashboard will be implemented here
        label = ctk.CTkLabel(
            dashboard_frame,
            text="Dashboard Panel - Under Construction",
            font=("Segoe UI", 16),
            text_color=self.colors['text_secondary']
        )
        label.pack(expand=True)
    
    def _toggle_connection(self):
        """Toggle bot connection"""
        if self.is_connected:
            self._disconnect()
        else:
            self._connect()
    
    def _connect(self):
        """Connect to services"""
        # Implementation will be added
        self.is_connected = True
        self.connect_btn.configure(
            text="🔌 Disconnect",
            fg_color=self.colors['accent_red']
        )
        self.connection_status.configure(
            text="Connected",
            text_color=self.colors['accent_green']
        )
        self.connection_indicator.configure(text_color=self.colors['accent_green'])
    
    def _disconnect(self):
        """Disconnect from services"""
        # Implementation will be added
        self.is_connected = False
        self.connect_btn.configure(
            text="🔗 Connect",
            fg_color=self.colors['accent_green']
        )
        self.connection_status.configure(
            text="Disconnected",
            text_color=self.colors['accent_red']
        )
        self.connection_indicator.configure(text_color=self.colors['accent_red'])
    
    def _send_command(self):
        """Send command from input"""
        command = self.command_entry.get()
        if command:
            self._log_activity(f"Command sent: {command}")
            self.command_entry.delete(0, tk.END)
    
    def _refresh_data(self):
        """Refresh data"""
        self._log_activity("Data refreshed")
    
    def _clear_chat(self):
        """Clear chat display"""
        self.chat_display.delete(1.0, tk.END)
        self._log_activity("Chat cleared")
    
    def _show_stats(self):
        """Show statistics"""
        self._log_activity("Statistics displayed")
    
    def _test_ai(self):
        """Test AI response"""
        self._log_activity("AI test initiated")
    
    def _log_activity(self, message):
        """Log activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
    
    def _open_settings(self):
        """Open settings window"""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.root, self.config, self.colors)
        self.settings_window.show()
    
    def _show_setup_wizard(self):
        """Show the OAuth setup wizard"""
        try:
            if self.oauth_wizard is None:
                self.oauth_wizard = OAuthSetupWizard(
                    parent=self.root,
                    config=self.config,
                    colors=self.colors,
                    on_complete=self._on_wizard_complete
                )
            
            self.oauth_wizard.show()
            logger.info("🧙 OAuth setup wizard opened")
            
        except Exception as e:
            logger.error(f"❌ OAuth wizard error: {e}")
            messagebox.showerror("Setup Error", f"Failed to open setup wizard: {e}")
    
    def _on_wizard_complete(self):
        """Handle completion of the OAuth setup wizard"""
        try:
            # Mark setup as complete
            self.config.mark_setup_complete()
            
            # Update first run status
            self.first_run = False
            
            # Show success message
            messagebox.showinfo(
                "Setup Complete", 
                "Your Stream Artifact bot has been configured successfully!\n\n"
                "Click 'Connect' to start your bot."
            )
            
            # Start connection if we have valid config
            if self.config.has_valid_config():
                self.root.after(1000, self._connect)
            
            logger.info("✅ Setup wizard completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Setup completion error: {e}")
            messagebox.showerror("Setup Error", f"Failed to complete setup: {e}")
    
    def _is_configured(self) -> bool:
        """Check if the application is properly configured"""
        return self.config.has_valid_config()
    
    def show(self):
        """Show the window"""
        if self.root:
            self.root.deiconify()
    
    def hide(self):
        """Hide the window"""
        if self.root:
            self.root.withdraw()
    
    def run(self):
        """Run the main window"""
        try:
            self.create_window()
            self.root.mainloop()
        except Exception as e:
            logger.error(f"❌ Window error: {e}")
            raise
    
    def destroy(self):
        """Destroy the window"""
        if self.root:
            self.root.destroy()
            self.root = None
    
    def _apply_brand_theme(self):
        """Apply the brand theme to CTk widgets"""
        # This ensures all CTk widgets use our brand colors by default
        import customtkinter as ctk
        
        # Update CTk's internal theme with our brand colors
        ctk.ThemeManager.theme["CTkButton"]["fg_color"] = [self.colors['button_bg'], self.colors['button_bg']]
        ctk.ThemeManager.theme["CTkButton"]["hover_color"] = [self.colors['button_hover'], self.colors['button_hover']]
        ctk.ThemeManager.theme["CTkButton"]["text_color"] = [self.colors['text_primary'], self.colors['text_primary']]
        
        ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = [self.colors['input_bg'], self.colors['input_bg']]
        ctk.ThemeManager.theme["CTkEntry"]["border_color"] = [self.colors['input_border'], self.colors['input_border']]
        ctk.ThemeManager.theme["CTkEntry"]["text_color"] = [self.colors['text_primary'], self.colors['text_primary']]
        
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [self.colors['bg_secondary'], self.colors['bg_secondary']]
        ctk.ThemeManager.theme["CTkFrame"]["border_color"] = [self.colors['border_color'], self.colors['border_color']]
        
        ctk.ThemeManager.theme["CTkProgressBar"]["fg_color"] = [self.colors['bg_tertiary'], self.colors['bg_tertiary']]
        ctk.ThemeManager.theme["CTkProgressBar"]["progress_color"] = [self.colors['accent_primary'], self.colors['accent_primary']]
