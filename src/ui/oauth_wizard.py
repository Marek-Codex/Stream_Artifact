"""
OAuth Setup Wizard for Stream Artifact
Simplified wrapper for the modular setup wizard
"""

from .setup_wizard import SetupWizard

# For backwards compatibility, export SetupWizard as OAuthSetupWizard
OAuthSetupWizard = SetupWizard
