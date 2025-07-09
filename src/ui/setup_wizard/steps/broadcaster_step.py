"""
Broadcaster Account Step for Setup Wizard
Connect the main Twitch broadcaster account (REQUIRED)
"""

import webbrowser
import secrets
from tkinter import messagebox

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel


class BroadcasterStep(BaseStep):
    """Broadcaster account connection step"""
    
    def get_title(self) -> str:
        return "🎬 Connect Your Broadcaster Account (Required)"
    
    def show(self):
        """Show the broadcaster connection step"""
        self.update_title(self.get_title())
        
        broadcaster_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        broadcaster_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Instructions
        instr_label = StandardLabel(
            broadcaster_frame,
            text="Connect your main Twitch account (the one you stream from).\\n"
                 "This is required for the bot to function.",
            font=("Segoe UI", 14),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        instr_label.pack(pady=20)
        
        # Connection status
        status_text = "✅ Connected" if self.wizard_data.get('broadcaster_connected') else "❌ Not connected"
        status_color = self.colors['success_color'] if self.wizard_data.get('broadcaster_connected') else self.colors['error_color']
        
        status_label = StandardLabel(
            broadcaster_frame,
            text=status_text,
            font=("Segoe UI", 14, "bold"),
            text_color=status_color
        )
        status_label.pack(pady=10)
        
        # Show username if connected
        if self.wizard_data.get('broadcaster_username'):
            username_label = StandardLabel(
                broadcaster_frame,
                text=f"Account: {self.wizard_data['broadcaster_username']}",
                font=("Segoe UI", 12),
                text_color=self.colors['text_secondary']
            )
            username_label.pack(pady=5)
        
        # Connect button
        button_text = "🔄 Reconnect Account" if self.wizard_data.get('broadcaster_connected') else "🔗 Connect Broadcaster Account"
        self.create_action_button(
            broadcaster_frame,
            button_text,
            self._connect_broadcaster,
            primary=True
        )
        
        # Info about what we'll access
        self.create_info_section(
            broadcaster_frame,
            "WHAT WE'LL ACCESS",
            [
                "👤 Your username and profile information",
                "💬 Permission to read chat messages",
                "📊 Basic channel information",
                "🔐 Secure OAuth connection (no password needed)"
            ],
            "🔒"
        )
    
    def _connect_broadcaster(self):
        """Connect broadcaster account via OAuth"""
        try:
            # For demo purposes, simulate the OAuth flow
            # In production, this would open a real OAuth URL
            messagebox.showinfo(
                "OAuth Connection",
                "Opening browser to connect your Twitch account...\\n"
                "Please authorize the application and return to this window."
            )
            
            # Simulate successful connection (replace with real OAuth)
            self._simulate_connection()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
    
    def _simulate_connection(self):
        """Simulate successful connection (for demo)"""
        import random
        
        # In production, this data would come from the OAuth callback
        self.wizard_data['broadcaster_connected'] = True
        self.wizard_data['broadcaster_username'] = f"streamer_{random.randint(1000, 9999)}"
        self.wizard_data['broadcaster_token'] = f"oauth:token_{random.randint(10000, 99999)}"
        
        # Refresh the display
        self.show()
        
        messagebox.showinfo("Success", "Broadcaster account connected successfully!")
    
    def validate(self) -> bool:
        """Validate broadcaster connection"""
        if not self.wizard_data.get('broadcaster_connected'):
            messagebox.showwarning(
                "Connection Required", 
                "You must connect your broadcaster account to continue.\\n"
                "This is required for the bot to access your chat."
            )
            return False
        return True
    
    def can_skip(self) -> bool:
        return False  # Cannot skip broadcaster connection
