# src/ui/panels/dashboard_panel.py
import customtkinter as ctk
from typing import TYPE_CHECKING

from .base_panel import BasePanel

if TYPE_CHECKING:
    from ...core.app import StreamArtifact # Assuming app.py contains StreamArtifact

class DashboardPanel(BasePanel):
    def __init__(self, parent, app: 'StreamArtifact', colors, logger):
        super().__init__(parent, app, colors, logger)
        self.logger.info("🎨 DashboardPanel initialized")

    def build_ui(self):
        """Build the UI for the Dashboard panel."""
        title_label = ctk.CTkLabel(
            self,
            text="📈 Dashboard",
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors.get('text_primary', '#FFFFFF')
        )
        title_label.pack(pady=10, padx=20, anchor="nw")

        placeholder_label = ctk.CTkLabel(
            self,
            text="Dashboard content will be implemented here.\n"
                 "This panel will display key stream analytics, bot statistics, and activity summaries.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_secondary', '#d4d4d4'),
            justify="left"
        )
        placeholder_label.pack(pady=20, padx=20, expand=True, fill="both")

    def on_show(self):
        self.logger.debug("DashboardPanel is now visible. Refreshing data (placeholder).")
        # Placeholder: In the future, this would trigger data loading for the dashboard
        # For example: self.app.analytics_manager.fetch_dashboard_data(callback=self._update_dashboard_widgets)
        pass

    def _update_dashboard_widgets(self, data):
        # Placeholder: Method to update dashboard widgets with new data
        self.logger.debug(f"Dashboard data received: {data}")
        pass
