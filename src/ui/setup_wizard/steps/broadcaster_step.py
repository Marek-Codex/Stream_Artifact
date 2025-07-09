"""
Broadcaster Account Step for Setup Wizard
Connect the main Twitch broadcaster account (REQUIRED)
"""

import webbrowser
import secrets # Used for state in real OAuth, might not be needed for simulation
from tkinter import messagebox
from typing import TYPE_CHECKING

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel # StandardButton via helper

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class BroadcasterStep(BaseStep):
    """Broadcaster account connection step"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # `self.app` can be used here to initiate the OAuth flow via `app.oauth_manager` or similar
        # For now, we'll keep the simulation but acknowledge `self.app` is available.

    def get_title(self) -> str:
        return "🎬 Connect Your Broadcaster Account (Required)"
    
    def show(self):
        """Show the broadcaster connection step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display
        
        broadcaster_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        broadcaster_frame.pack(fill="both", expand=True, padx=40, pady=20) # Reduced pady
        
        # Instructions
        instr_label = StandardLabel(
            broadcaster_frame,
            text="Connect your main Twitch account (the one you stream from).\n"
                 "This is required for the bot to function.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center"
        )
        instr_label.pack(pady=15) # Adjusted pady
        
        # Connection status display
        is_connected = self.wizard_data.get('broadcaster_connected', False)
        status_text = "✅ Connected" if is_connected else "❌ Not connected"
        status_color_key = 'success_color' if is_connected else 'error_color'
        
        status_label = StandardLabel(
            broadcaster_frame,
            text=status_text,
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors.get(status_color_key, 'red') # Fallback to red
        )
        status_label.pack(pady=10)
        
        # Show username if connected
        if is_connected and self.wizard_data.get('broadcaster_username'):
            username_label = StandardLabel(
                broadcaster_frame,
                text=f"Account: {self.wizard_data['broadcaster_username']}",
                font=("Segoe UI", 12),
                text_color=self.colors.get('text_secondary', '#d4d4d4')
            )
            username_label.pack(pady=(0,10)) # Adjusted pady
        
        # Connect/Reconnect button
        button_text = "🔄 Reconnect Account" if is_connected else "🔗 Connect Broadcaster Account"
        self.create_action_button( # Helper from BaseStep
            broadcaster_frame,
            button_text,
            self._initiate_broadcaster_connection, # Renamed method
            primary=True, # Main action button for this step
            width=300 # Wider button
        )
        
        # Info about what permissions are needed
        self.create_info_section( # Helper from BaseStep
            broadcaster_frame,
            "Permissions We Need", # Title for info section
            [
                "👤 Your username and basic profile information.",
                "💬 Permission to read your channel's chat messages.",
                "📊 Access to basic channel information (e.g., stream status).",
                "🔐 Secure OAuth connection (we never see or store your password)."
            ],
            "🔒" # Icon
        )
    
    def _initiate_broadcaster_connection(self):
        """Initiate the OAuth flow for the broadcaster account."""
        # TODO: Replace simulation with actual OAuth flow using self.app
        # Example (conceptual):
        # if self.app and hasattr(self.app, 'oauth_manager'):
        #     try:
        #         # The oauth_manager should handle opening browser, local server, and callback
        #         # It should return user_info (username, token) upon success
        #         user_info = await self.app.oauth_manager.authenticate_user(
        #             user_type='broadcaster', # To differentiate if scopes are different
        #             on_success_callback=self._on_oauth_success,
        #             on_failure_callback=self._on_oauth_failure
        #         )
        #         # If using async/await, this step needs to handle it, or wizard needs to manage async tasks
        #     except Exception as e:
        #         self._on_oauth_failure(str(e))
        # else:
        #     messagebox.showerror("Error", "OAuth manager not available in the application.", parent=self.wizard.window)
        #     self._simulate_connection() # Fallback to simulation if app/oauth_manager is not ready

        messagebox.showinfo(
            "OAuth Simulation",
            "This would normally open your browser to Twitch for authentication.\n"
            "Simulating a successful connection for now.",
            parent=self.wizard.window
        )
        self._simulate_connection() # Keep simulation for now

    def _on_oauth_success(self, token: str, username: str, user_type: str):
        """Callback for successful OAuth authentication."""
        if user_type == 'broadcaster':
            self.wizard_data['broadcaster_connected'] = True
            self.wizard_data['broadcaster_username'] = username
            self.wizard_data['broadcaster_token'] = token # Ensure it includes "oauth:" prefix if needed by API
            
            # Log success (using wizard's logger or app's logger)
            logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
            if logger:
                logger.info(f"Broadcaster account '{username}' connected successfully via OAuth.")

            self._refresh_step_ui() # Refresh UI to show connected status
            messagebox.showinfo("Success", f"Broadcaster account '{username}' connected!", parent=self.wizard.window)
        else:
            # Handle unexpected user_type if necessary
            pass

    def _on_oauth_failure(self, error_message: str):
        """Callback for failed OAuth authentication."""
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.error(f"Broadcaster OAuth connection failed: {error_message}")
        messagebox.showerror("Connection Error", f"Failed to connect broadcaster account: {error_message}", parent=self.wizard.window)
        self._refresh_step_ui() # Refresh UI to show disconnected status

    def _simulate_connection(self):
        """Simulate successful OAuth connection (for development/testing)."""
        import random
        # This data would come from the OAuth callback in a real flow
        username = f"streamer_{random.randint(1000, 9999)}"
        token = f"oauth:simulated_token_{secrets.token_hex(8)}" # Generate a fake token
        self._on_oauth_success(token, username, 'broadcaster')

    def _refresh_step_ui(self):
        """Clears and re-renders the content for this step."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.show()

    def save_data(self):
        """
        Data (token, username, connected status) is saved directly into self.wizard_data
        by the _on_oauth_success or _simulate_connection methods.
        No further action needed here.
        """
        pass
    
    def validate(self) -> bool:
        """Validate that the broadcaster account is connected."""
        if not self.wizard_data.get('broadcaster_connected'):
            messagebox.showwarning(
                "Connection Required", 
                "You must connect your broadcaster account to continue.\n"
                "This is required for the bot to access your chat and function correctly.",
                parent=self.wizard.window
            )
            return False
        return True
    
    def can_skip(self) -> bool:
        return False  # Broadcaster connection is mandatory.
