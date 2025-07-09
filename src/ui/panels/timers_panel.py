# src/ui/panels/timers_panel.py
import customtkinter as ctk
from typing import TYPE_CHECKING

from .base_panel import BasePanel

if TYPE_CHECKING:
    from ...core.app import StreamArtifact

class TimersPanel(BasePanel):
    def __init__(self, parent, app: 'StreamArtifact', colors, logger):
        super().__init__(parent, app, colors, logger)
        self.logger.info("🎨 TimersPanel initialized")

    def build_ui(self):
        """Build the UI for the Timers panel."""
        title_label = ctk.CTkLabel(
            self,
            text="⏰ Timed Messages",
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors.get('text_primary', '#FFFFFF')
        )
        title_label.pack(pady=10, padx=20, anchor="nw")

        placeholder_label = ctk.CTkLabel(
            self,
            text="Set up automated messages to be sent to chat at regular intervals.\n"
                 "You'll be able to configure the message content, timing interval, and chat line requirements.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_secondary', '#d4d4d4'),
            justify="left"
        )
        placeholder_label.pack(pady=20, padx=20, expand=True, fill="both")

    def on_show(self):
        self.logger.debug("TimersPanel is now visible. Loading timers (placeholder).")
        # Placeholder: self.app.timer_manager.load_timers()
        pass

    def on_hide(self):
        self.logger.debug("TimersPanel is now hidden. Saving timers (placeholder).")
        # Placeholder: self.app.timer_manager.save_timers()
        pass
