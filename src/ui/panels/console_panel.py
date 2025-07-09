# src/ui/panels/console_panel.py
import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
from datetime import datetime
import logging

from .base_panel import BasePanel

class ConsolePanel(BasePanel):
    def __init__(self, parent, app, colors, logger):
        super().__init__(parent, app, colors, logger)
        self.logger.info("🎨 ConsolePanel initialized")

    def build_ui(self):
        # Create vertical layout for sections
        # Top section: Chat and activity
        top_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_secondary'])
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Bottom section: Quick actions and stats
        bottom_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_secondary'], height=200)
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
            font=("Consolas", 10),
            state=tk.DISABLED # Start as read-only
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=5)

        # Create tabbed interface for bottom section
        bottom_notebook = ctk.CTkTabview(
            bottom_frame,
            fg_color=self.colors['bg_tertiary'],
            segmented_button_fg_color=self.colors['bg_primary'],
            segmented_button_selected_color=self.colors['accent_primary'],
            segmented_button_selected_hover_color=self.colors['accent_primary_hover'],
            segmented_button_unselected_color=self.colors['bg_tertiary'],
            segmented_button_unselected_hover_color=self.colors['hover_color'],
        )
        bottom_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        bottom_notebook.add("Activity Log")
        bottom_notebook.add("Bot Status")
        bottom_notebook.add("Quick Commands")

        # Activity Log tab
        activity_frame = bottom_notebook.tab("Activity Log")
        self.activity_log = scrolledtext.ScrolledText(
            activity_frame,
            height=8,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_secondary'],
            font=("Consolas", 9),
            state=tk.DISABLED # Start as read-only
        )
        self.activity_log.pack(fill="both", expand=True, padx=5, pady=5)

        # Bot Status tab
        status_frame = bottom_notebook.tab("Bot Status")
        self._create_bot_status_section(status_frame)

        # Quick Commands tab
        commands_frame = bottom_notebook.tab("Quick Commands")
        self._create_quick_commands_section(commands_frame)

        # Make the main_window the source of truth for these logging methods for now
        if hasattr(self.app.main_window, 'log_message_to_chat_display'):
            self.app.main_window.chat_display_widget = self.chat_display
        if hasattr(self.app.main_window, 'log_activity'):
             self.app.main_window.activity_log_widget = self.activity_log


    def _create_bot_status_section(self, parent_frame):
        parent = ctk.CTkFrame(parent_frame, fg_color="transparent")
        parent.pack(fill="both", expand=True)

        status_grid = ctk.CTkFrame(parent, fg_color="transparent")
        status_grid.pack(fill="both", expand=True, padx=10, pady=10)

        # Status items
        # These will need to be updated dynamically from the app core
        self.status_widgets = {}
        status_items = [
            ("Connection", "❌ Disconnected", "accent_red"),
            ("Uptime", "00:00:00", "text_secondary"),
            ("Messages Sent", "0", "text_secondary"),
            ("Commands Processed", "0", "text_secondary"),
            ("AI Responses", "0", "text_secondary"),
            ("Errors", "0", "accent_red")
        ]

        for i, (label, value, color_key) in enumerate(status_items):
            row = i // 3
            col = i % 3

            item_frame = ctk.CTkFrame(status_grid, fg_color=self.colors['bg_primary'])
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            label_widget = ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Segoe UI", 10),
                text_color=self.colors['text_muted']
            )
            label_widget.pack(pady=(5,2))

            value_widget = ctk.CTkLabel(
                item_frame,
                text=value,
                font=("Segoe UI", 12, "bold"),
                text_color=self.colors[color_key]
            )
            value_widget.pack(pady=(2,5))
            self.status_widgets[label.lower().replace(" ", "_")] = value_widget

        for i in range(2): # Rows
             status_grid.grid_rowconfigure(i, weight=1)
        for i in range(3): # Columns
            status_grid.grid_columnconfigure(i, weight=1)

    def _create_quick_commands_section(self, parent_frame):
        parent = ctk.CTkFrame(parent_frame, fg_color="transparent")
        parent.pack(fill="both", expand=True)

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
        self.command_entry.pack(side="left", padx=10, pady=10, expand=True)

        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self._send_command_from_ui, # Renamed to avoid conflict if main_window has _send_command
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
            ("🔄 Refresh", self._refresh_data_ui),
            ("🧹 Clear Chat", self._clear_chat_ui),
            ("📊 Stats", self._show_stats_ui),
            ("🎯 Test AI", self._test_ai_ui)
        ]

        for text, command in quick_actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                height=35,
                fg_color=self.colors['bg_tertiary'],
                hover_color=self.colors['button_hover']
            )
            btn.pack(side="left", padx=5, pady=10, expand=True, fill="x")

    def _send_command_from_ui(self):
        command = self.command_entry.get()
        if command:
            # This should ideally call a method in self.app or self.app.twitch_client
            self.logger.info(f"UI: Command sent: {command}")
            if hasattr(self.app.main_window, 'log_activity'):
                self.app.main_window.log_activity(f"Command sent: {command}")
            self.command_entry.delete(0, tk.END)

    def _refresh_data_ui(self):
        self.logger.info("UI: Data refresh requested")
        if hasattr(self.app.main_window, 'log_activity'):
            self.app.main_window.log_activity("Data refreshed")

    def _clear_chat_ui(self):
        self.logger.info("UI: Clear chat requested")
        if hasattr(self.app.main_window, 'clear_chat_display'): # Check if main_window has this method
            self.app.main_window.clear_chat_display()
        elif hasattr(self.app.main_window, 'chat_display_widget'): # Fallback to direct widget manipulation
             self.app.main_window.chat_display_widget.configure(state=tk.NORMAL)
             self.app.main_window.chat_display_widget.delete(1.0, tk.END)
             self.app.main_window.chat_display_widget.configure(state=tk.DISABLED)

        if hasattr(self.app.main_window, 'log_activity'):
            self.app.main_window.log_activity("Chat cleared")


    def _show_stats_ui(self):
        self.logger.info("UI: Show stats requested")
        # This should probably trigger a display of stats, maybe in a new window or this panel
        if hasattr(self.app.main_window, 'log_activity'):
            self.app.main_window.log_activity("Statistics displayed (placeholder)")

    def _test_ai_ui(self):
        self.logger.info("UI: Test AI requested")
        # This should trigger an AI test, e.g., send a predefined message to the AI
        if hasattr(self.app.main_window, 'log_activity'):
            self.app.main_window.log_activity("AI test initiated (placeholder)")

    def on_show(self):
        self.logger.debug("ConsolePanel is now visible")
        # You might want to refresh some data here

    def update_status(self, status_key: str, value: str, color_key: str = None):
        """Update a status widget in the Bot Status section."""
        if status_key in self.status_widgets:
            self.status_widgets[status_key].configure(text=value)
            if color_key and color_key in self.colors:
                self.status_widgets[status_key].configure(text_color=self.colors[color_key])
        else:
            self.logger.warning(f"Status key '{status_key}' not found in status_widgets.")

    # Methods to be called from MainWindow or App Core to update the UI
    def log_message_to_chat(self, message: str):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def log_to_activity_feed(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.configure(state=tk.NORMAL)
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
        self.activity_log.configure(state=tk.DISABLED)

    def clear_chat_display_widget(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state=tk.DISABLED)
