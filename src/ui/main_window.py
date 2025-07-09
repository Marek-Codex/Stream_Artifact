"""
Main Window for Stream Artifact
Professional interface with resizable sections and comprehensive options
"""

import tkinter as tk
from tkinter import ttk, messagebox # scrolledtext might be used by ConsolePanel directly
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
from .oauth_wizard import OAuthSetupWizard # Ensure this is the correct wizard class
from .panels.base_panel import BasePanel # Import BasePanel for type hinting if needed
from .panels.console_panel import ConsolePanel
from .panels.dashboard_panel import DashboardPanel
from .panels.commands_panel import CommandsPanel
from .panels.timers_panel import TimersPanel
# Future panels:

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window with a modular panel-based interface."""

    def __init__(self, app):
        self.app = app
        self.config = app.config
        self.root: Optional[ctk.CTk] = None
        self.is_running = False

        # UI Components
        self.settings_window: Optional[SettingsWindow] = None
        self.oauth_wizard: Optional[OAuthSetupWizard] = None # Or your specific wizard class
        self.status_bar: Optional[ctk.CTkFrame] = None
        self.connection_status_label: Optional[ctk.CTkLabel] = None # For status bar
        self.connect_button: Optional[ctk.CTkButton] = None # For header
        self.connection_indicator_dot: Optional[ctk.CTkLabel] = None # For sidebar header

        # Panel Management
        self.sidebar: Optional[ctk.CTkFrame] = None
        self.main_content_area: Optional[ctk.CTkFrame] = None # Frame to pack panels into
        self.panel_title_label: Optional[ctk.CTkLabel] = None
        self.current_panel_id: str = "console" # Default panel
        self.active_panel_widget: Optional[BasePanel] = None # Current visible panel
        self.panels_cache: Dict[str, BasePanel] = {} # Cache for instantiated panels
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        # Helper attributes for ConsolePanel interactions (might be phased out)
        # self.chat_display: Optional[scrolledtext.ScrolledText] = None # Managed by ConsolePanel
        # self.activity_log: Optional[scrolledtext.ScrolledText] = None # Managed by ConsolePanel

        # Connection state - primarily managed by app core, reflected in UI
        self.is_connected: bool = False
        self.connection_thread = None # Likely managed by app core
        self.first_run = self.config.is_first_run() # Or use setup_complete flag

        self._setup_theme()
        logger.info("🎨 Main window initialized")

    def _setup_theme(self):
        """Setup the theme based on config or defaults."""
        # Using a simplified color definition for brevity in this example
        self.colors = {
            'bg_primary': self.config.get('theme', 'bg_primary', '#0a0a0a'),
            'bg_secondary': self.config.get('theme', 'bg_secondary', '#1a1a1a'),
            'bg_tertiary': self.config.get('theme', 'bg_tertiary', '#2a2a2a'),
            'sidebar_bg': self.config.get('theme', 'sidebar_bg', '#151515'),
            'text_primary': self.config.get('theme', 'text_primary', '#ffffff'),
            'text_secondary': self.config.get('theme', 'text_secondary', '#d4d4d4'),
            'text_muted': self.config.get('theme', 'text_muted', '#9d9d9d'),
            'border_color': self.config.get('theme', 'border_color', '#404040'),
            'accent_primary': self.config.get('theme', 'accent_primary', '#3CA0FF'),
            'accent_primary_hover': self.config.get('theme', 'accent_primary_hover', '#5fb3ff'),
            'accent_green': self.config.get('theme', 'accent_green', '#4ade80'),
            'accent_red': self.config.get('theme', 'accent_red', '#f87171'),
            'accent_orange': self.config.get('theme', 'accent_orange', '#fbbf24'),
            'button_bg': self.config.get('theme', 'button_bg', '#3CA0FF'),
            'button_hover': self.config.get('theme', 'button_hover', '#5fb3ff'),
            'input_bg': self.config.get('theme', 'input_bg', '#2a2a2a'),
            'input_border': self.config.get('theme', 'input_border', '#404040'),
            'scrollbar_thumb': self.config.get('theme', 'scrollbar_thumb', '#404040'),
            'scrollbar_hover': self.config.get('theme', 'scrollbar_hover', '#505050'), # Corrected key
            'online_color': self.config.get('theme', 'online_color', '#4ade80'),
            'offline_color': self.config.get('theme', 'offline_color', '#6b7280'), # Generic gray
            'hover_color': self.config.get('theme', 'hover_color', '#2a2a2a'), # For nav buttons
        }
        # Add any missing essential colors with defaults if not in config
        self.colors.setdefault('accent_blue', self.colors['accent_primary'])


        ctk.set_appearance_mode(self.config.get('ui', 'appearance_mode', "dark"))
        ctk.set_default_color_theme(self.config.get('ui', 'color_theme', "blue")) # or a custom theme file
        # self._apply_brand_theme() # This might be too aggressive; apply colors selectively or use a theme file

    def create_window(self):
        """Create the main application window."""
        self.root = ctk.CTk()
        self.root.title(self.config.get('app', 'title', "Stream Artifact"))
        # Use config for geometry, with a default
        default_geometry = "1400x900"
        # geometry = self.config.get('ui', 'window_geometry', default_geometry) # Example
        self.root.geometry(default_geometry)
        self.root.configure(fg_color=self.colors['bg_primary'])

        try:
            # Resolve path relative to this file's location more robustly
            assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
            icon_path = assets_dir / "Chibi_Construct.png" # Ensure this is the correct icon name
            if icon_path.exists():
                icon_image = Image.open(icon_path)
                # For Windows title bar icon (usually .ico)
                ico_path = assets_dir / "app_icon.ico" # Assuming you might have an .ico
                if ico_path.exists() and os.name == 'nt':
                     self.root.iconbitmap(default=str(ico_path))
                else: # For taskbar icon / other OS (usually .png)
                    # Resize for good quality in taskbar, e.g., 64x64 or 128x128
                    icon_photo = ImageTk.PhotoImage(icon_image.resize((64, 64), Image.Resampling.LANCZOS))
                    self.root.iconphoto(True, icon_photo)
                    self.app_icon_photo = icon_photo # Keep reference
            else:
                logger.warning(f"Application icon not found at {icon_path}")
        except Exception as e:
            logger.warning(f"Could not load application icon: {e}")

        self.root.minsize(1024, 768) # Sensible minimum size
        self.root.protocol("WM_DELETE_WINDOW", self.app.on_close) # Handle close via app

        self._create_layout()

        # Determine if setup wizard should run
        if self.config.is_first_run() or not self.config.get('app', 'setup_complete', False):
            logger.info("First run or setup not complete. Scheduling setup wizard.")
            self.root.after(200, self._show_setup_wizard) # Short delay
        else:
            logger.info("Setup previously completed. Skipping wizard.")
            # Attempt to auto-connect if configured, handled by app.py
            # self.app.schedule_coroutine(self.app.try_auto_connect())

        logger.info("🪟 Main window created and configured.")

    def _create_layout(self):
        """Create the main window layout: sidebar, content area, status bar."""
        # Main container to hold sidebar and content area
        main_app_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_app_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self._create_sidebar(main_app_frame)
        self._create_main_content_holder(main_app_frame) # Renamed for clarity
        self._create_status_bar() # Status bar at the bottom of self.root

    def _create_sidebar(self, parent_frame):
        """Create the sidebar with header, navigation, and bottom controls."""
        self.sidebar = ctk.CTkFrame(parent_frame, width=250, fg_color=self.colors['sidebar_bg'], corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=(0,1), pady=0) # Pad only on right
        self.sidebar.pack_propagate(False)

        # Sidebar Header (App Title & Connection Status)
        sidebar_header = ctk.CTkFrame(self.sidebar, height=60, fg_color=self.colors['bg_secondary'], corner_radius=0)
        sidebar_header.pack(fill="x", pady=(0,1)) # Pad only on bottom
        sidebar_header.pack_propagate(False)
        
        title_container = ctk.CTkFrame(sidebar_header, fg_color="transparent")
        title_container.pack(expand=True, fill="both", padx=10)


        try:
            assets_dir = Path(__file__).resolve().parent.parent.parent / "assets"
            sidebar_icon_path = assets_dir / "Chibi_Construct.png"
            if sidebar_icon_path.exists():
                sidebar_img = Image.open(sidebar_icon_path).resize((28, 28), Image.Resampling.LANCZOS)
                self.sidebar_icon = ImageTk.PhotoImage(sidebar_img) # Keep reference
                icon_lbl = ctk.CTkLabel(title_container, image=self.sidebar_icon, text="")
                icon_lbl.pack(side="left", padx=(0, 5))
        except Exception as e:
            logger.warning(f"Could not load sidebar icon: {e}")

        app_title_lbl = ctk.CTkLabel(title_container, text=self.config.get('app', 'title', "Stream Artifact"), font=("Segoe UI", 16, "bold"), text_color=self.colors['text_primary'])
        app_title_lbl.pack(side="left", padx=5)

        self.connection_indicator_dot = ctk.CTkLabel(title_container, text="●", font=("Segoe UI", 16), text_color=self.colors['offline_color'])
        self.connection_indicator_dot.pack(side="right", padx=5)

        self._create_navigation_menu(self.sidebar) # Pass sidebar as parent

        # Sidebar Bottom (Settings & Wizard Buttons)
        sidebar_bottom = ctk.CTkFrame(self.sidebar, height=90, fg_color=self.colors['bg_secondary'], corner_radius=0) # Reduced height
        sidebar_bottom.pack(fill="x", side="bottom")
        sidebar_bottom.pack_propagate(False)
        
        bottom_buttons_container = ctk.CTkFrame(sidebar_bottom, fg_color="transparent")
        bottom_buttons_container.pack(expand=True, pady=5)

        settings_btn = ctk.CTkButton(
            bottom_buttons_container, text="⚙️ Settings", command=self._open_settings_window, width=180, height=35,
            fg_color=self.colors['button_bg'], hover_color=self.colors['button_hover']
        )
        settings_btn.pack(pady=(5,2))

        wizard_btn = ctk.CTkButton(
            bottom_buttons_container, text="🧙 Setup Wizard", command=self._show_setup_wizard, width=180, height=35,
            fg_color=self.colors['accent_orange'], hover_color=self.colors.get('accent_orange_hover', self.colors['accent_orange'])
        )
        wizard_btn.pack(pady=(2,5))

    def _create_navigation_menu(self, parent_frame):
        """Create the scrollable navigation menu in the sidebar."""
        nav_scrollable_frame = ctk.CTkScrollableFrame(
            parent_frame, fg_color="transparent",
            scrollbar_button_color=self.colors['scrollbar_thumb'],
            scrollbar_button_hover_color=self.colors['scrollbar_hover']
        )
        nav_scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.panel_definitions = self._get_panel_definitions()
        self.nav_buttons = {}

        for panel_def in self.panel_definitions:
            btn = ctk.CTkButton(
                nav_scrollable_frame, text=panel_def['display_name'],
                command=lambda pid=panel_def['id']: self.switch_to_panel(pid),
                height=35, fg_color="transparent", hover_color=self.colors.get('hover_color', self.colors['bg_tertiary']),
                text_color=self.colors['text_secondary'], anchor="w", font=("Segoe UI", 12)
            )
            btn.pack(fill="x", pady=2, padx=2)
            self.nav_buttons[panel_def['id']] = btn
        
        self._update_active_nav_button(self.current_panel_id)

    def _get_panel_definitions(self) -> List[Dict[str, str]]:
        """Returns a list of panel definitions (id, display_name)."""
        # This could be loaded from a config file or defined here
        return [
            {"id": "console", "display_name": "📊 Console"},
            {"id": "dashboard", "display_name": "📈 Dashboard"},
            {"id": "commands", "display_name": "💬 Commands"},
            {"id": "timers", "display_name": "⏰ Timers"},
            {"id": "quotes", "display_name": "💭 Quotes"},
            # Add all other panels here...
            {"id": "discord", "display_name": "🔗 Discord"}
        ]

    def _create_main_content_holder(self, parent_frame):
        """Create the area where panels are displayed, including its header."""
        content_holder_frame = ctk.CTkFrame(parent_frame, fg_color=self.colors['bg_primary'], corner_radius=0)
        content_holder_frame.pack(side="left", fill="both", expand=True, padx=(1,0), pady=0) # Pad only on left

        # Header for the content area (Panel Title & Connect Button)
        content_header = ctk.CTkFrame(content_holder_frame, height=50, fg_color=self.colors['bg_secondary'], corner_radius=0)
        content_header.pack(fill="x", pady=(0,1)) # Pad only on bottom
        content_header.pack_propagate(False)

        self.panel_title_label = ctk.CTkLabel(content_header, text="Console", font=("Segoe UI", 18, "bold"), text_color=self.colors['text_primary'])
        self.panel_title_label.pack(side="left", padx=15, pady=10)

        # Connect button container (allows for more buttons later if needed)
        connect_button_frame = ctk.CTkFrame(content_header, fg_color="transparent")
        connect_button_frame.pack(side="right", padx=15, pady=5)
        
        self.connect_button = ctk.CTkButton(
            connect_button_frame, text="🔗 Connect", command=self._handle_toggle_connection, width=120, height=35,
            fg_color=self.colors['accent_green'], hover_color=self.colors.get('accent_green_hover', self.colors['accent_green'])
        )
        self.connect_button.pack()

        # Area where the actual panel widgets will be packed
        self.main_content_area = ctk.CTkFrame(content_holder_frame, fg_color="transparent")
        self.main_content_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.switch_to_panel(self.current_panel_id) # Display the initial panel

    def _create_status_bar(self):
        """Create the status bar at the bottom of the root window."""
        self.status_bar = ctk.CTkFrame(self.root, height=25, fg_color=self.colors['bg_secondary'], corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom", pady=(1,0)) # Pad only on top
        self.status_bar.pack_propagate(False)

        status_text_lbl = ctk.CTkLabel(self.status_bar, text="Ready", font=("Segoe UI", 10), text_color=self.colors['text_secondary'])
        status_text_lbl.pack(side="left", padx=10)
        self.status_text_widget = status_text_lbl # Keep a reference if needed

        self.connection_status_label = ctk.CTkLabel(self.status_bar, text="Disconnected", font=("Segoe UI", 10), text_color=self.colors['offline_color'])
        self.connection_status_label.pack(side="right", padx=10)

    def switch_to_panel(self, panel_id: str):
        """Switches the visible panel in the main content area."""
        logger.debug(f"Attempting to switch to panel: {panel_id}")
        if self.active_panel_widget and hasattr(self.active_panel_widget, 'on_hide'):
            self.active_panel_widget.on_hide()
        if self.active_panel_widget:
            self.active_panel_widget.pack_forget()

        self.current_panel_id = panel_id
        
        panel_to_display = None
        if panel_id in self.panels_cache:
            panel_to_display = self.panels_cache[panel_id]
            logger.debug(f"Loading {panel_id} from cache.")
        else:
            logger.debug(f"Creating new instance for {panel_id}.")
            panel_constructor = self._get_panel_constructor(panel_id)
            if panel_constructor:
                panel_to_display = panel_constructor(self.main_content_area, self.app, self.colors, logger)
                self.panels_cache[panel_id] = panel_to_display
            else: # Fallback to a placeholder if panel not implemented
                logger.warning(f"No constructor for panel '{panel_id}'. Using placeholder.")
                panel_to_display = self._create_placeholder_panel_widget(panel_id)
                # self.panels_cache[panel_id] = panel_to_display # Optionally cache placeholders

        if panel_to_display:
            self.active_panel_widget = panel_to_display
            self.active_panel_widget.pack(in_=self.main_content_area, fill="both", expand=True)
            if hasattr(self.active_panel_widget, 'on_show'):
                self.active_panel_widget.on_show()
        else: # Should not happen if placeholder is effective
             logger.error(f"Failed to create or find panel: {panel_id}")


        current_panel_def = next((p for p in self.panel_definitions if p['id'] == panel_id), None)
        panel_display_name = current_panel_def['display_name'].split(" ",1)[1] if current_panel_def and " " in current_panel_def['display_name'] else panel_id.title()
        self.panel_title_label.configure(text=panel_display_name)
        
        self._update_active_nav_button(panel_id)

    def _get_panel_constructor(self, panel_id: str) -> Optional[Callable]:
        """Returns the constructor for a given panel_id."""
        panel_map = {
            "console": ConsolePanel,
            # "dashboard": DashboardPanel, # Add other panels here
            # "commands": CommandsPanel,
        }
        return panel_map.get(panel_id)

    def _create_placeholder_panel_widget(self, panel_id: str) -> BasePanel:
        """Creates a standard placeholder panel."""
        # Using BasePanel itself can work if its build_ui shows a placeholder
        # Or a dedicated PlaceholderPanel class could be made.
        class PlaceholderPanel(BasePanel):
            def build_ui(self):
                label = ctk.CTkLabel(self, text=f"{panel_id.title()} Panel - Not Yet Implemented",
                                     font=("Segoe UI", 16), text_color=self.colors['text_muted'])
                label.pack(expand=True, padx=20, pady=20)

        return PlaceholderPanel(self.main_content_area, self.app, self.colors, logger)


    def _update_active_nav_button(self, active_panel_id: str):
        """Updates the visual state of navigation buttons."""
        for panel_id, button in self.nav_buttons.items():
            if panel_id == active_panel_id:
                button.configure(fg_color=self.colors['accent_blue'], text_color=self.colors['text_primary'])
            else:
                button.configure(fg_color="transparent", text_color=self.colors['text_secondary'])
    
    # Methods removed as their functionality is now in ConsolePanel or app core:
    # _create_console_panel, _create_bot_status_section, _create_quick_commands_section
    # _send_command, _refresh_data, _clear_chat, _show_stats, _test_ai, _log_activity

    # Connection handling should be done via app core, which then calls update_connection_ui
    def _handle_toggle_connection(self):
        """Sends toggle connection request to the main app."""
        if self.app:
            self.app.toggle_connection_services() # App core handles logic and calls back update_connection_ui
        else:
            logger.error("Application core not available to toggle connection.")
            # Fallback UI update (not recommended as state desyncs)
            # self.update_connection_ui(not self.is_connected, "Error: App offline")


    def update_connection_ui(self, is_connected: bool, status_message: str = ""):
        """Updates all UI elements related to connection status. Called by App."""
        self.is_connected = is_connected
        default_status_message = "Connected" if is_connected else "Disconnected"
        final_status_message = status_message or default_status_message

        if is_connected:
            self.connect_button.configure(text="🔌 Disconnect", fg_color=self.colors['accent_red'])
            self.connection_status_label.configure(text=final_status_message, text_color=self.colors['online_color'])
            self.connection_indicator_dot.configure(text_color=self.colors['online_color'])
            if self.status_text_widget: self.status_text_widget.configure(text="Running")
        else:
            self.connect_button.configure(text="🔗 Connect", fg_color=self.colors['accent_green'])
            self.connection_status_label.configure(text=final_status_message, text_color=self.colors['offline_color'])
            self.connection_indicator_dot.configure(text_color=self.colors['offline_color'])
            if self.status_text_widget: self.status_text_widget.configure(text="Ready")

        # If console panel is active and is a ConsolePanel, update its status too
        if self.current_panel_id == "console" and isinstance(self.active_panel_widget, ConsolePanel):
            conn_status_text = "✅ Connected" if is_connected else "❌ Disconnected"
            conn_color = 'online_color' if is_connected else 'offline_color'
            self.active_panel_widget.update_status("connection", conn_status_text, conn_color)
        logger.info(f"Connection UI updated: {final_status_message}")


    # Methods to interact with ConsolePanel (if active)
    def post_message_to_chat_display(self, message: str, sender: str = "System", color_key: Optional[str] = None):
        """Posts a message to the chat display if ConsolePanel is active."""
        if self.current_panel_id == "console" and isinstance(self.active_panel_widget, ConsolePanel):
            # The ConsolePanel's log_message_to_chat can be enhanced to handle sender/color
            self.active_panel_widget.log_message_to_chat(f"[{sender}]: {message}")
        else:
            logger.debug(f"Chat message '{message}' not shown: Console panel not active.")

    def post_activity_log(self, message: str):
        """Posts a message to the activity log if ConsolePanel is active."""
        if self.current_panel_id == "console" and isinstance(self.active_panel_widget, ConsolePanel):
            self.active_panel_widget.log_to_activity_feed(message)
        else:
            logger.debug(f"Activity log '{message}' not shown: Console panel not active.")
            
    def trigger_clear_chat_display(self):
        """Clears the chat display if ConsolePanel is active."""
        if self.current_panel_id == "console" and isinstance(self.active_panel_widget, ConsolePanel):
            self.active_panel_widget.clear_chat_display_widget()
            self.post_activity_log("Chat display cleared.")


    def _open_settings_window(self): # Renamed
        """Opens the settings window, ensuring only one instance."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self.root, self.app, self.colors, logger) # Pass app
            self.settings_window.show() # SettingsWindow should handle its own display logic
        else:
            self.settings_window.lift_and_focus() # Method in SettingsWindow to bring to front

    def _show_setup_wizard(self):
        """Shows the setup wizard, ensuring only one instance."""
        # Dynamic import if SetupWizard is complex or to break cycles
        from .setup_wizard.wizard_main import SetupWizard

        if self.oauth_wizard is None or not (self.oauth_wizard.window and self.oauth_wizard.window.winfo_exists()): # Check window too
            self.oauth_wizard = SetupWizard( # Use the actual wizard class name
                parent=self.root,
                app=self.app, # Pass app object
                config=self.config, # Config object
                colors=self.colors,
                on_complete=self._on_setup_wizard_complete # Renamed callback
            )
            self.oauth_wizard.show() # Wizard handles its display
            logger.info("🧙 Setup wizard shown.")
        else:
            if hasattr(self.oauth_wizard, 'lift_and_focus'): # Check if method exists
                self.oauth_wizard.lift_and_focus() # Wizard needs this method
            else: # Fallback if method not implemented on wizard yet
                self.oauth_wizard.window.lift()
                self.oauth_wizard.window.focus_force()
            logger.info("🧙 Existing setup wizard brought to front.")

    def _on_setup_wizard_complete(self):
        """Callback for when the setup wizard finishes."""
        try:
            # Config 'setup_complete' is set by the wizard itself before calling on_complete.
            # self.config.set('app', 'setup_complete', True) # Already done by wizard
            # self.config.save() # Already done by wizard

            self.first_run = False # Update runtime state of MainWindow

            messagebox.showinfo(
                "Setup Complete",
                "Configuration saved successfully!\n\n"
                "If this was the first time setup, a restart might be beneficial for all changes to take effect.\n"
                "Otherwise, you can now connect the bot if credentials are valid."
            )
            logger.info("✅ Setup wizard reported completion to MainWindow.")
            
            # Update UI to reflect that setup is done
            # This might involve re-checking config and enabling/disabling features
            # For now, just ensure connection UI is in a sensible default state.
            if self.app:
                 asyncio.run_coroutine_threadsafe(self.app.initialize_clients_from_config(), self.app.event_loop)
            self.update_connection_ui(False) # Reset to disconnected, ready to connect

        except Exception as e:
            logger.error(f"❌ Error in MainWindow after setup wizard completion: {e}", exc_info=True)
            messagebox.showerror("Setup Error", f"An error occurred in MainWindow after setup: {e}")

    def show(self):
        """Ensures the main window is visible."""
        if self.root and not self.root.winfo_viewable():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def hide(self):
        """Hides the main window."""
        if self.root:
            self.root.deiconify()
    
    def hide(self):
        """Hide the window"""
        if self.root and self.root.winfo_viewable():
            self.root.withdraw()

    def run(self):
        """Creates (if necessary) and runs the main application loop."""
        try:
            if not self.root:
                self.create_window()
            if self.root: # Ensure root was created successfully
                 self.is_running = True
                 self.root.mainloop()
            else:
                logger.critical("Root window not created. Application cannot run.")
        except Exception as e:
            logger.critical(f"❌ Unhandled error in main window run: {e}", exc_info=True)
            # Optionally, attempt a graceful shutdown or error dialog
        finally:
            self.is_running = False # Mark as not running
            logger.info("⏹️ Main window event loop terminated.")


    def destroy(self):
        """Destroys the main window and cleans up associated resources."""
        logger.info("Destroying main window and child components...")
        if self.oauth_wizard and self.oauth_wizard.window and self.oauth_wizard.window.winfo_exists():
            try:
                self.oauth_wizard.window.destroy()
            except Exception as e:
                logger.error(f"Error destroying oauth_wizard: {e}")
        self.oauth_wizard = None

        if self.settings_window and self.settings_window.winfo_exists():
            try:
                self.settings_window.destroy()
            except Exception as e:
                logger.error(f"Error destroying settings_window: {e}")
        self.settings_window = None
        
        # Destroy cached panels
        for panel_id, panel_widget in self.panels_cache.items():
            if panel_widget and panel_widget.winfo_exists():
                try:
                    panel_widget.destroy()
                except Exception as e:
                    logger.error(f"Error destroying panel {panel_id}: {e}")
        self.panels_cache.clear()


        if self.root and self.root.winfo_exists():
            try:
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error destroying root window: {e}")
        self.root = None
        logger.info("Main window and resources destroyed.")

    def _apply_brand_theme(self):
        """
        DEPRECATED or use with caution. Modifying ThemeManager directly is generally not recommended
        for themes that should be switchable or component-specific.
        Prefer styling widgets directly or using CustomTkinter's JSON theme files.
        """
        logger.warning("'_apply_brand_theme' directly modifies CTk ThemeManager, consider alternatives.")
        # Example: ctk.ThemeManager.theme["CTkButton"]["fg_color"] = [self.colors['button_bg'], self.colors['button_bg']]
        # This method is kept for reference but should ideally be replaced.
        pass
