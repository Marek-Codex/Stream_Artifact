"""
Standard UI Widgets for Stream Artifact
Professional widgets without glowing effects or rounded corners
"""

import customtkinter as ctk
from typing import Dict, Optional, Callable
import tkinter as tk


class StandardFrame(ctk.CTkFrame):
    """Standard frame without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardButton(ctk.CTkButton):
    """Standard button without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardLabel(ctk.CTkLabel):
    """Standard label without effects"""
    
    def __init__(self, parent, **kwargs):
        # Remove any glow effects
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardEntry(ctk.CTkEntry):
    """Standard entry without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardCombobox(ctk.CTkComboBox):
    """Standard combobox without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardSwitch(ctk.CTkSwitch):
    """Standard switch"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)


class StandardScrollableFrame(ctk.CTkScrollableFrame):
    """Standard scrollable frame without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardProgressBar(ctk.CTkProgressBar):
    """Standard progress bar without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardTabview(ctk.CTkTabview):
    """Standard tabview without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


class StandardTextbox(ctk.CTkTextbox):
    """Standard textbox without rounded corners"""
    
    def __init__(self, parent, **kwargs):
        # Remove rounded corners
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = 0
        super().__init__(parent, **kwargs)


# Aliases for backward compatibility
ProfessionalFrame = StandardFrame
ProfessionalButton = StandardButton
ProfessionalLabel = StandardLabel
ProfessionalEntry = StandardEntry
ProfessionalCombobox = StandardCombobox
ProfessionalSwitch = StandardSwitch
