"""
Cloud Backup Step for Setup Wizard
Configure cloud backup (OPTIONAL)
"""

import webbrowser
from tkinter import messagebox

from .base_step import BaseStep
from ...components.standard_widgets import StandardFrame, StandardLabel, StandardButton


class BackupStep(BaseStep):
    """Cloud backup configuration step (optional)"""
    
    def get_title(self) -> str:
        return "☁️ Cloud Backup (Optional)"
    
    def show(self):
        """Show the cloud backup step"""
        self.update_title(self.get_title())
        
        backup_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        backup_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Friendly intro
        intro_label = StandardLabel(
            backup_frame,
            text="☁️ Keep your settings safe and sync across devices!\n"
                 "This is completely optional - local storage works great too.",
            font=("Segoe UI", 14),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        intro_label.pack(pady=20)
        
        # Options frame
        options_frame = StandardFrame(
            backup_frame,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_tertiary'],
            border_width=2
        )
        options_frame.pack(fill="x", pady=20)
        
        # Local storage option (default)
        local_section = StandardFrame(
            options_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['success_color'],
            border_width=1
        )
        local_section.pack(fill="x", padx=20, pady=15)
        
        local_title = StandardLabel(
            local_section,
            text="💾 Local Storage Only (Recommended)",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['success_color']
        )
        local_title.pack(pady=10)
        
        local_desc = StandardLabel(
            local_section,
            text="✅ Completely free and private\n"
                 "✅ No external accounts needed\n"
                 "✅ Your data never leaves your computer\n"
                 "❌ No sync across devices",
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        local_desc.pack(pady=5, padx=20)
        
        local_btn = StandardButton(
            local_section,
            text="✅ Use Local Storage",
            command=self._select_local_storage,
            width=200,
            height=40,
            fg_color=self.colors['success_color']
        )
        local_btn.pack(pady=15)
        
        # GitHub backup option
        github_section = StandardFrame(
            options_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['accent_secondary'],
            border_width=1
        )
        github_section.pack(fill="x", padx=20, pady=15)
        
        github_title = StandardLabel(
            github_section,
            text="🔗 GitHub Backup (Advanced)",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors['accent_secondary']
        )
        github_title.pack(pady=10)
        
        github_desc = StandardLabel(
            github_section,
            text="✅ Sync across multiple devices\n"
                 "✅ Automatic backups to private GitHub gists\n"
                 "✅ Version history and restore points\n"
                 "💡 Requires free GitHub account",
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        github_desc.pack(pady=5, padx=20)
        
        github_btn = StandardButton(
            github_section,
            text="🔗 Connect GitHub",
            command=self._connect_github,
            width=200,
            height=40,
            fg_color=self.colors['accent_secondary']
        )
        github_btn.pack(pady=15)
        
        # Status
        self.status_label = StandardLabel(
            backup_frame,
            text="💾 Using local storage (default)",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['success_color']
        )
        self.status_label.pack(pady=20)
        
        # Update status if GitHub is configured
        if self.wizard_data.get('github_token'):
            self.status_label.configure(
                text="✅ GitHub backup configured",
                text_color=self.colors['success_color']
            )
    
    def _select_local_storage(self):
        """Select local storage option"""
        self.wizard_data['backup_type'] = 'local'
        self.wizard_data['backup_configured'] = True
        
        self.status_label.configure(
            text="💾 Using local storage",
            text_color=self.colors['success_color']
        )
        
        messagebox.showinfo(
            "Local Storage Selected",
            "✅ Your bot will store all settings locally on this computer.\n\n"
            "This is completely free and keeps your data private!"
        )
    
    def _connect_github(self):
        """Connect to GitHub for backup"""
        # Show info about GitHub backup
        result = messagebox.askyesno(
            "GitHub Backup",
            "🔗 This will connect to your GitHub account to:\n\n"
            "• Create private gists for your bot settings\n"
            "• Sync settings across devices\n"
            "• Provide automatic backups\n\n"
            "GitHub accounts are free and this won't cost you anything.\n\n"
            "Continue to GitHub?"
        )
        
        if result:
            # Direct link to GitHub (they can sign up if needed)
            webbrowser.open("https://github.com/settings/tokens")
            
            # Show instruction
            messagebox.showinfo(
                "GitHub Setup",
                "📝 Next steps:\n\n"
                "1. Sign up for GitHub if you don't have an account\n"
                "2. Go to Settings > Developer settings > Personal access tokens\n"
                "3. Create a token with 'gist' scope\n"
                "4. Come back and enter the token\n\n"
                "💡 GitHub accounts are completely free!"
            )
    
    def can_skip(self) -> bool:
        return True
    
    def skip(self):
        """Mark backup as skipped"""
        self.wizard_data['skip_backup'] = True
        self.wizard_data['backup_type'] = 'local'
