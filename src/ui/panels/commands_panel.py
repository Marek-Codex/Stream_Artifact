# src/ui/panels/commands_panel.py
import customtkinter as ctk
from typing import TYPE_CHECKING

from .base_panel import BasePanel

if TYPE_CHECKING:
    from ...core.app import StreamArtifact

class CommandsPanel(BasePanel):
    def __init__(self, parent, app: 'StreamArtifact', colors, logger):
        super().__init__(parent, app, colors, logger)
        self.logger.info("🎨 CommandsPanel initialized")

    def build_ui(self):
        """Build the UI for the Commands panel."""
        title_label = ctk.CTkLabel(
            self,
            text="💬 Custom Commands",
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors.get('text_primary', '#FFFFFF')
        )
        title_label.pack(pady=10, padx=20, anchor="nw")

        placeholder_label = ctk.CTkLabel(
            self,
            text="Manage your custom chat commands here.\n"
                 "You'll be able to add, edit, delete, and set permissions for commands.\n"
                 "Features like command cooldowns, aliases, and cost (if currency is enabled) will be available.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_secondary', '#d4d4d4'),
            justify="left"
        )
        placeholder_label.pack(pady=20, padx=20, expand=True, fill="both")

    def on_show(self):
        self.logger.debug("CommandsPanel is now visible. Loading commands (placeholder).")
        # Placeholder: self.app.command_manager.load_commands()
        pass

    def on_hide(self):
        self.logger.debug("CommandsPanel is now hidden. Saving commands (placeholder).")
        # Placeholder: self.app.command_manager.save_commands()
        pass
