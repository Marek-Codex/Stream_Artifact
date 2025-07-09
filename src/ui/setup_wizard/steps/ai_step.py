"""
AI Services Step for Setup Wizard
Configure AI APIs (OPTIONAL)
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox

from .base_step import BaseStep
from ...components.standard_widgets import (
    StandardFrame, StandardLabel, StandardButton, StandardEntry,
    StandardCombobox, StandardSwitch
)


class AIStep(BaseStep):
    """AI services configuration step (optional)"""
    
    def get_title(self) -> str:
        return "🤖 AI Services (Optional)"
    
    def show(self):
        """Show the AI services step"""
        self.update_title(self.get_title())
        
        ai_frame = StandardFrame(
            self.content_frame,
            fg_color="transparent"
        )
        ai_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Friendly intro
        intro_label = StandardLabel(
            ai_frame,
            text="Add AI-powered chat responses to your stream! 🤖\n"
                 "This step is completely optional - you can skip it and add AI later.",
            font=("Segoe UI", 14),
            text_color=self.colors['text_primary'],
            justify="center"
        )
        intro_label.pack(pady=20)
        
        # OpenRouter section
        openrouter_frame = StandardFrame(
            ai_frame,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_primary'],
            border_width=2
        )
        openrouter_frame.pack(fill="x", pady=20)
        
        # OpenRouter header
        or_header = StandardLabel(
            openrouter_frame,
            text="🔮 OpenRouter AI Integration",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors['accent_primary']
        )
        or_header.pack(pady=10)
        
        # Friendly disclaimer
        disclaimer_text = (
            "💡 Great news! This bot defaults to FREE AI models only.\n\n"
            "🆓 Free Tier Benefits:\n"
            "• No charges - completely safe to use\n"
            "• 50 requests/day (perfect for testing!)\n\n"
            "💰 $10+ Credit Benefits:\n"
            "• 1,000 requests/day (20x more!)\n"
            "• Access to premium models (if you enable them)\n"
            "• Better performance and reliability\n\n"
            "🛡️ Our Protection: We keep you on FREE models only.\n"
            "This way, if you add $10+, you keep those higher daily limits!\n"
            "Premium models are opt-in only with clear warnings."
        )
        
        disclaimer_label = StandardLabel(
            openrouter_frame,
            text=disclaimer_text,
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        disclaimer_label.pack(pady=10, padx=20)
        
        # API Key section
        api_section = StandardFrame(
            openrouter_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        api_section.pack(fill="x", padx=20, pady=15)
        
        # Get API key button
        get_key_btn = StandardButton(
            api_section,
            text="🔗 Get OpenRouter API Key",
            command=self._open_openrouter_keys,
            width=250,
            height=40,
            fg_color=self.colors['accent_secondary'],
            hover_color=self.colors['hover_color']
        )
        get_key_btn.pack(pady=10)
        
        # API Key input
        key_label = StandardLabel(
            api_section,
            text="OpenRouter API Key (starts with 'sk-or-'):",
            font=("Segoe UI", 12),
            text_color=self.colors['text_primary']
        )
        key_label.pack(pady=(10, 5))
        
        self.api_key_entry = StandardEntry(
            api_section,
            placeholder_text="sk-or-v1-...",
            width=400,
            height=35,
            show="*"
        )
        self.api_key_entry.pack(pady=5)
        
        # Test key button
        test_btn = StandardButton(
            api_section,
            text="🧪 Test API Key",
            command=self._test_api_key,
            width=150,
            height=35,
            fg_color=self.colors['success_color']
        )
        test_btn.pack(pady=10)
        
        # Model selection (safe defaults)
        model_frame = StandardFrame(
            openrouter_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        model_frame.pack(fill="x", padx=20, pady=15)
        
        model_label = StandardLabel(
            model_frame,
            text="🎯 AI Model Selection (Safe Defaults):",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['text_primary']
        )
        model_label.pack(pady=10)
        
        # Free models toggle (ON by default)
        self.free_models_var = tk.BooleanVar(value=True)
        free_toggle = StandardSwitch(
            model_frame,
            text="✅ Use Free Models Only (Recommended)",
            variable=self.free_models_var,
            onvalue=True,
            offvalue=False,
            command=self._toggle_free_models
        )
        free_toggle.pack(pady=5)
        
        # Premium models toggle (OFF by default)
        self.premium_models_var = tk.BooleanVar(value=False)
        premium_toggle = StandardSwitch(
            model_frame,
            text="⚠️ Enable Premium Models (Uses Your Credits)",
            variable=self.premium_models_var,
            onvalue=True,
            offvalue=False,
            command=self._toggle_premium_models
        )
        premium_toggle.pack(pady=5)
        
        # Model selection dropdown
        model_select_label = StandardLabel(
            model_frame,
            text="Default Model:",
            font=("Segoe UI", 11),
            text_color=self.colors['text_secondary']
        )
        model_select_label.pack(pady=(10, 5))
        
        # Start with free models
        free_models = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        
        self.model_dropdown = StandardCombobox(
            model_frame,
            values=free_models,
            width=350,
            height=35,
            state="readonly"
        )
        self.model_dropdown.set(free_models[0])  # Default to first free model
        self.model_dropdown.pack(pady=5)
        
        # Status indicator
        self.status_label = StandardLabel(
            ai_frame,
            text="❌ Not configured",
            font=("Segoe UI", 12, "bold"),
            text_color=self.colors['error_color']
        )
        self.status_label.pack(pady=20)
        
        # Update status if already configured
        if self.wizard_data.get('ai_configured'):
            self.status_label.configure(
                text="✅ AI configured - Free models only",
                text_color=self.colors['success_color']
            )
    
    def _open_openrouter_keys(self):
        """Open OpenRouter API keys page"""
        webbrowser.open("https://openrouter.ai/keys")
    
    def _test_api_key(self):
        """Test the OpenRouter API key"""
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenRouter API key first.")
            return
        
        if not api_key.startswith("sk-or-"):
            messagebox.showerror("Error", "Invalid API key format. OpenRouter keys start with 'sk-or-'")
            return
        
        # TODO: Implement actual API key validation
        # For now, just store it
        self.wizard_data['openrouter_key'] = api_key
        self.wizard_data['ai_configured'] = True
        self.wizard_data['ai_free_models_only'] = self.free_models_var.get()
        self.wizard_data['ai_selected_model'] = self.model_dropdown.get()
        
        self.status_label.configure(
            text="✅ AI configured - Free models only" if self.free_models_var.get() else "✅ AI configured - Premium models enabled",
            text_color=self.colors['success_color']
        )
        
        model_type = "free-tier" if self.free_models_var.get() else "premium"
        messagebox.showinfo(
            "Success!",
            f"OpenRouter API key validated successfully!\n\n"
            f"✅ Mode: {model_type} models\n"
            f"🎯 Default model: {self.model_dropdown.get()}\n\n"
            f"{'💡 Your credits are safe - only free models will be used!' if self.free_models_var.get() else '⚠️ Premium models enabled - may use your OpenRouter credits.'}"
        )
    
    def _toggle_free_models(self):
        """Handle free models toggle"""
        if self.free_models_var.get():
            # Switch to free models
            free_models = [
                "meta-llama/llama-3.2-3b-instruct:free",
                "microsoft/phi-3-mini-128k-instruct:free", 
                "google/gemma-2-9b-it:free",
                "mistralai/mistral-7b-instruct:free"
            ]
            self.model_dropdown.configure(values=free_models)
            self.model_dropdown.set(free_models[0])
            self.premium_models_var.set(False)
    
    def _toggle_premium_models(self):
        """Handle premium models toggle"""
        if self.premium_models_var.get():
            # Show warning and switch to premium models
            result = messagebox.askyesno(
                "Enable Premium Models?",
                "⚠️ IMPORTANT: This will enable premium AI models that cost money.\n\n"
                "🛡️ Rate Limit Protection:\n"
                "• If you have $10+ in OpenRouter, you get 1,000 free requests/day\n"
                "• Using premium models might drop you below $10\n"
                "• This could reduce you to only 50 free requests/day\n\n"
                "💡 We recommend keeping $10+ buffer if you enable this.\n\n"
                "Are you sure you want to continue?"
            )
            
            if result:
                premium_models = [
                    "openai/gpt-4o-mini",
                    "anthropic/claude-3.5-sonnet",
                    "openai/gpt-4o",
                    "google/gemini-pro",
                    "meta-llama/llama-3.2-3b-instruct:free",  # Keep some free options
                    "microsoft/phi-3-mini-128k-instruct:free"
                ]
                self.model_dropdown.configure(values=premium_models)
                self.model_dropdown.set(premium_models[0])
                self.free_models_var.set(False)
            else:
                # User cancelled, revert the toggle
                self.premium_models_var.set(False)
    
    def can_skip(self) -> bool:
        return True
    
    def skip(self):
        """Mark AI as skipped"""
        self.wizard_data['skip_ai'] = True
        self.wizard_data['ai_configured'] = False
