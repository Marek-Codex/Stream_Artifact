# src/ui/panels/base_panel.py
import customtkinter as ctk

class BasePanel(ctk.CTkFrame):
    def __init__(self, parent, app, colors, logger, **kwargs):
        super().__init__(parent, fg_color=colors['bg_primary'], **kwargs)
        self.app = app
        self.config = app.config
        self.colors = colors
        self.logger = logger
        self.build_ui()

    def build_ui(self):
        """
        This method should be overridden by subclasses to create the panel's UI.
        """
        # Example:
        # label = ctk.CTkLabel(self, text=f"{self.__class__.__name__} - Implement me!")
        # label.pack(expand=True, padx=20, pady=20)
        pass

    def on_show(self):
        """
        Called when the panel is shown. Override to refresh data or perform actions.
        """
        pass

    def on_hide(self):
        """
        Called when the panel is hidden. Override to stop updates or save state.
        """
        pass
