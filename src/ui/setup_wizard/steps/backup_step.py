"""
Cloud Backup Step for Setup Wizard
Configure cloud backup (OPTIONAL)
"""

import webbrowser
from tkinter import messagebox
from typing import TYPE_CHECKING, Optional

from .base_step import BaseStep
# Assuming StandardEntry and StandardCombobox might be used if UI evolves
from ...components.standard_widgets import StandardFrame, StandardLabel, StandardButton, StandardEntry, StandardCombobox

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact


class BackupStep(BaseStep):
    """Cloud backup configuration step (optional)"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        self.status_label: Optional[StandardLabel] = None
        # Add self.github_token_entry if/when an entry field is added directly to this step.
        # For now, this step might just guide the user to settings post-setup if they choose GitHub.

    def get_title(self) -> str:
        return "☁️ Cloud Backup (Optional)"
    
    def show(self):
        """Show the cloud backup step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display
        
        backup_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        backup_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        intro_label = StandardLabel(
            backup_frame,
            text="☁️ Keep your settings safe and sync across devices!\n"
                 "This is completely optional - local storage works great too.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center",
            wraplength=backup_frame.winfo_width() - 40 if backup_frame.winfo_width() > 50 else 500
        )
        intro_label.pack(pady=(0,15))
        
        options_frame = StandardFrame(
            backup_frame, fg_color=self.colors.get('bg_tertiary', '#2a2a2a'),
            border_color=self.colors.get('accent_tertiary', self.colors.get('border_color', '#FF6B9D')), # Use accent or default
            border_width=1, corner_radius=5 # Reduced border width
        )
        options_frame.pack(fill="x", pady=10)
        
        # --- Local Storage Option ---
        local_section = self._create_option_section(
            options_frame,
            title="💾 Local Storage Only (Recommended)",
            description_points=[
                "✅ Completely free and private.",
                "✅ No external accounts or setup needed.",
                "✅ Your data never leaves your computer.",
                "❌ No automatic sync across multiple devices."
            ],
            button_text="✅ Use Local Storage",
            button_command=self._select_local_storage,
            button_fg_color=self.colors.get('success_color', 'green')
        )
        
        # --- GitHub Backup Option ---
        # Note: This step currently doesn't have an entry for the GitHub token.
        # It implies configuration would happen later or assumes a token is already set.
        # For a full setup, an entry field would be needed here if 'GitHub Gist' is chosen.
        github_section = self._create_option_section(
            options_frame,
            title="🔗 GitHub Gist Backup (Advanced)",
            description_points=[
                "✅ Sync settings across multiple devices.",
                "✅ Automatic backups to a private GitHub Gist.",
                "✅ Version history and easy restore points.",
                "💡 Requires a free GitHub account and a Personal Access Token."
            ],
            button_text="🔗 Configure GitHub Backup",
            button_command=self._configure_github_backup, # This might open a sub-dialog or guide
            button_fg_color=self.colors.get('accent_secondary', 'blue')
        )
        
        # --- Status Label ---
        self.status_label = StandardLabel(
            backup_frame, text="Current: Using local storage (default)",
            font=("Segoe UI", 12, "italic"), text_color=self.colors.get('text_muted', 'gray')
        )
        self.status_label.pack(pady=10)
        self._update_backup_status_display() # Set initial status

    def _create_option_section(self, parent_frame, title, description_points, button_text, button_command, button_fg_color):
        """Helper to create a consistent UI for each backup option."""
        section = StandardFrame(
            parent_frame, fg_color=self.colors.get('bg_primary_alt', self.colors.get('bg_primary', '#0a0a0a')),
            border_color=self.colors.get('border_light', '#505050'), border_width=1, corner_radius=3
        )
        section.pack(fill="x", padx=15, pady=10)
        
        StandardLabel(section, text=title, font=("Segoe UI", 13, "bold"), text_color=button_fg_color).pack(pady=(8,4))
        
        for point in description_points:
            StandardLabel(section, text=point, font=("Segoe UI", 10), text_color=self.colors.get('text_secondary'), justify="left", anchor="w").pack(pady=1, padx=15, anchor="w")

        self.create_action_button(section, button_text, button_command, primary=False, fg_color=button_fg_color, text_color=self.colors.get('text_inverse_on_accent', 'black'), width=220).pack(pady=(8,8))
        return section

    def _select_local_storage(self):
        """Selects local storage as the backup option."""
        self.wizard_data['backup_type'] = 'local'
        self.wizard_data['github_token'] = '' # Clear any GitHub token
        self.wizard_data['backup_configured'] = False # False could mean "no cloud backup configured"
        self._update_backup_status_display()
        messagebox.showinfo("Local Storage Selected", "Settings will be stored locally on this computer.", parent=self.wizard.window)

    def _configure_github_backup(self):
        """Guides user or opens UI to configure GitHub backup."""
        # This is where you'd ideally open a small dialog to input the GitHub token,
        # or guide the user to the main settings if this wizard step is just informational.
        # For now, it will just set the type and prompt for token input post-wizard.
        
        # Let's assume for now it just sets the type and user has to add token later in settings.
        self.wizard_data['backup_type'] = 'github'
        # We don't set backup_configured to True yet, as token is missing.
        
        messagebox.showinfo(
            "GitHub Backup Selected",
            "GitHub Gist backup selected.\n\n"
            "After completing the wizard, please go to:\n"
            "Settings -> Backup -> GitHub Gist\n"
            "to enter your Personal Access Token with 'gist' scope.\n\n"
            "You can get a token from: https://github.com/settings/tokens",
            parent=self.wizard.window
        )
        webbrowser.open("https://github.com/settings/tokens") # Open token page for convenience
        self._update_backup_status_display()

    def _update_backup_status_display(self):
        backup_type = self.wizard_data.get('backup_type', 'local')
        github_token_present = bool(self.wizard_data.get('github_token'))

        if backup_type == 'github':
            if github_token_present:
                status_text = "✅ Cloud Backup: GitHub Gist (Token Present)"
                color_key = 'success_color'
            else:
                status_text = "⚠️ Cloud Backup: GitHub Gist (Token Required in Settings)"
                color_key = 'warning_color'
        else: # local
            status_text = "💾 Backup: Local Storage Only"
            color_key = 'info_color' # Or text_secondary

        if self.status_label:
            self.status_label.configure(text=status_text, text_color=self.colors.get(color_key, 'gray'))

    def save_data(self):
        """Saves the chosen backup type. Token is handled by _configure_github_backup or main settings."""
        # backup_type is set by _select_local_storage or _configure_github_backup
        # github_token might be set if a sub-dialog was used, or cleared if local.
        # backup_configured status depends on if token is valid for GitHub.

        # For this simplified version, 'backup_configured' will be true if github is selected AND token is present.
        if self.wizard_data.get('backup_type') == 'github':
            self.wizard_data['backup_configured'] = bool(self.wizard_data.get('github_token'))
        else:
            self.wizard_data['backup_configured'] = False # Or True if local is "configured"

        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
             logger.info(f"Backup step save_data: Type='{self.wizard_data.get('backup_type')}', Configured='{self.wizard_data.get('backup_configured')}'")
        self._update_backup_status_display()

    def can_skip(self) -> bool:
        return True # Backup configuration is optional.
    
    def skip(self):
        """Handle skipping backup configuration: defaults to Local Only."""
        self.wizard_data['skip_backup'] = True
        self.wizard_data['backup_type'] = 'local' # Default if skipped
        self.wizard_data['github_token'] = ''
        self.wizard_data['backup_configured'] = False # Cloud backup not configured
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.info("Backup step skipped. Defaulting to Local Only backup.")
