"""
Cyberpunk UI Components for Stream Artifact
Custom widgets with glassmorphism and cyberpunk styling
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import math
from typing import Optional, Callable, Union


class CyberpunkFrame(ctk.CTkFrame):
    """Custom frame with cyberpunk styling and glassmorphism effects"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#1a1a2e',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 10
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        # Add subtle glow effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Add glow effect on hover"""
        self.configure(border_color="#00d4ff")
    
    def _on_leave(self, event):
        """Remove glow effect"""
        self.configure(border_color="#333366")


class CyberpunkButton(ctk.CTkButton):
    """Custom button with cyberpunk styling and effects"""
    
    def __init__(self, parent, glow_color: str = "#00d4ff", **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#16213e',
            'hover_color': '#2a2a4e',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 8,
            'text_color': '#ffffff',
            'font': ('Consolas', 12, 'bold')
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        self.glow_color = glow_color
        self.original_border_color = kwargs.get('border_color', '#333366')
        
        # Add hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _on_enter(self, event):
        """Add glow effect on hover"""
        self.configure(border_color=self.glow_color)
    
    def _on_leave(self, event):
        """Remove glow effect"""
        self.configure(border_color=self.original_border_color)
    
    def _on_click(self, event):
        """Click effect"""
        self.configure(border_color="#ffffff")
        self.after(100, lambda: self.configure(border_color=self.glow_color))


class CyberpunkLabel(ctk.CTkLabel):
    """Custom label with cyberpunk styling and optional glow effect"""
    
    def __init__(self, parent, glow_color: str = None, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'text_color': '#ffffff',
            'font': ('Consolas', 12)
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        self.glow_color = glow_color
        
        # Add glow effect if specified
        if glow_color:
            self._add_glow_effect()
    
    def _add_glow_effect(self):
        """Add text glow effect (simulated)"""
        # This is a simplified glow effect
        # In a more advanced implementation, you could use custom drawing
        pass


class CyberpunkEntry(ctk.CTkEntry):
    """Custom entry with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#0a0a0a',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 5,
            'text_color': '#ffffff',
            'placeholder_text_color': '#666666',
            'font': ('Consolas', 11)
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        # Add focus effects
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Add glow effect on focus"""
        self.configure(border_color="#00d4ff")
    
    def _on_focus_out(self, event):
        """Remove glow effect"""
        self.configure(border_color="#333366")


class CyberpunkTextbox(ctk.CTkTextbox):
    """Custom textbox with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#0a0a0a',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 5,
            'text_color': '#ffffff',
            'font': ('Consolas', 10)
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)
        
        # Add focus effects
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Add glow effect on focus"""
        self.configure(border_color="#00d4ff")
    
    def _on_focus_out(self, event):
        """Remove glow effect"""
        self.configure(border_color="#333366")


class CyberpunkProgressBar(ctk.CTkProgressBar):
    """Custom progress bar with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#0a0a0a',
            'progress_color': '#00d4ff',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 5,
            'height': 20
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)


class CyberpunkSwitch(ctk.CTkSwitch):
    """Custom switch with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#333366',
            'progress_color': '#00d4ff',
            'button_color': '#ffffff',
            'button_hover_color': '#e0e0e0',
            'text_color': '#ffffff',
            'font': ('Consolas', 11)
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)


class CyberpunkComboBox(ctk.CTkComboBox):
    """Custom combobox with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#0a0a0a',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 5,
            'text_color': '#ffffff',
            'font': ('Consolas', 11),
            'dropdown_fg_color': '#1a1a2e',
            'dropdown_text_color': '#ffffff',
            'dropdown_hover_color': '#333366'
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)


# Alias for consistency with settings window
CyberpunkCombobox = CyberpunkComboBox


class CyberpunkScrollableFrame(ctk.CTkScrollableFrame):
    """Custom scrollable frame with cyberpunk styling"""
    
    def __init__(self, parent, **kwargs):
        # Default cyberpunk styling
        default_kwargs = {
            'fg_color': '#1a1a2e',
            'border_color': '#333366',
            'border_width': 1,
            'corner_radius': 10,
            'scrollbar_fg_color': '#0a0a0a',
            'scrollbar_button_color': '#333366',
            'scrollbar_button_hover_color': '#00d4ff'
        }
        
        # Merge with provided kwargs
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        
        super().__init__(parent, **kwargs)


class GlowEffect:
    """Utility class for creating glow effects"""
    
    @staticmethod
    def create_glow_image(width: int, height: int, color: str = "#00d4ff", intensity: float = 0.5) -> ImageTk.PhotoImage:
        """Create a glow effect image"""
        # Create a new image with transparency
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Convert color to RGB
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        # Create gradient for glow effect
        center_x, center_y = width // 2, height // 2
        max_distance = min(center_x, center_y)
        
        for x in range(width):
            for y in range(height):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= max_distance:
                    alpha = int(255 * intensity * (1 - distance / max_distance))
                    image.putpixel((x, y), (*color_rgb, alpha))
        
        # Apply blur for smoother glow
        image = image.filter(ImageFilter.GaussianBlur(radius=2))
        
        return ImageTk.PhotoImage(image)


class CyberpunkWindow(ctk.CTkToplevel):
    """Custom window with cyberpunk styling"""
    
    def __init__(self, parent, title: str = "Stream Artifact", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configure window
        self.title(title)
        self.configure(fg_color="#0a0a0a")
        
        # Make window resizable
        self.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Add window effects
        self.attributes("-alpha", 0.95)  # Slight transparency for glass effect
        
        # Focus the window
        self.focus()
        self.grab_set()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class AnimatedButton(CyberpunkButton):
    """Button with animated effects"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.animation_active = False
        self.original_text = self.cget("text")
    
    def start_animation(self, text: str = "Processing..."):
        """Start loading animation"""
        if not self.animation_active:
            self.animation_active = True
            self.configure(text=text, state="disabled")
            self._animate_loading()
    
    def stop_animation(self):
        """Stop loading animation"""
        self.animation_active = False
        self.configure(text=self.original_text, state="normal")
    
    def _animate_loading(self):
        """Animate loading dots"""
        if self.animation_active:
            current_text = self.cget("text")
            if current_text.endswith("..."):
                self.configure(text=current_text[:-3])
            else:
                self.configure(text=current_text + ".")
            
            self.after(500, self._animate_loading)


class StatusIndicator(ctk.CTkLabel):
    """Status indicator with color-coded states"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.states = {
            'online': {'color': '#00ff41', 'text': '● ONLINE'},
            'offline': {'color': '#ff4444', 'text': '● OFFLINE'},
            'connecting': {'color': '#ffaa00', 'text': '● CONNECTING'},
            'error': {'color': '#ff4444', 'text': '● ERROR'}
        }
        
        self.set_state('offline')
    
    def set_state(self, state: str):
        """Set the status state"""
        if state in self.states:
            self.configure(
                text=self.states[state]['text'],
                text_color=self.states[state]['color']
            )
    
    def pulse(self):
        """Create a pulsing effect"""
        current_alpha = self.cget("text_color")
        # Implement pulsing animation
        pass
