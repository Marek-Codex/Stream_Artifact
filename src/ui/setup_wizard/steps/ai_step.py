"""
AI Services Step for Setup Wizard
Configure AI APIs (OPTIONAL)
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox
from typing import TYPE_CHECKING, List # Added List for type hinting

from .base_step import BaseStep
from ...components.standard_widgets import (
    StandardFrame, StandardLabel, StandardButton, StandardEntry,
    StandardCombobox, StandardSwitch
)

if TYPE_CHECKING:
    from ..wizard_main import SetupWizard
    from ....core.app import StreamArtifact # For app instance
    from ....ai.openrouter_client import OpenRouterClient # For AI client if used directly


class AIStep(BaseStep):
    """AI services configuration step (optional)"""

    def __init__(self, wizard: 'SetupWizard', app: 'StreamArtifact'):
        super().__init__(wizard, app)
        # UI elements that need to be accessed later
        self.api_key_entry: StandardEntry = None
        self.model_dropdown: StandardCombobox = None
        self.free_models_var: tk.BooleanVar = None
        self.premium_models_var: tk.BooleanVar = None
        self.status_label: StandardLabel = None
        # Store fetched models to avoid repeated API calls if key is unchanged
        self._fetched_models: List[str] = []
        self._current_api_key_for_fetched_models: str = ""

    def get_title(self) -> str:
        return "🤖 AI Services (Optional)"
    
    def show(self):
        """Show the AI services step content."""
        # self.update_wizard_main_title(self.get_title()) # Wizard handles full title display
        
        ai_frame = StandardFrame(
            self.content_frame, # Property from BaseStep
            fg_color="transparent"
        )
        ai_frame.pack(fill="both", expand=True, padx=20, pady=20) # Reduced padx/pady
        
        # Friendly intro
        intro_label = StandardLabel(
            ai_frame,
            text="Add AI-powered chat responses to your stream! 🤖\n"
                 "This step is completely optional - you can skip it and add AI later.",
            font=("Segoe UI", 14),
            text_color=self.colors.get('text_primary', '#FFFFFF'),
            justify="center"
        )
        intro_label.pack(pady=(0,15)) # Adjusted padding
        
        # --- OpenRouter Configuration Section ---
        openrouter_frame = StandardFrame(
            ai_frame,
            fg_color=self.colors.get('bg_tertiary', '#2a2a2a'),
            border_color=self.colors.get('accent_primary', '#3CA0FF'),
            border_width=1, # Reduced border
            corner_radius=5
        )
        openrouter_frame.pack(fill="x", pady=10) # Reduced pady
        
        or_header = StandardLabel(
            openrouter_frame,
            text="🔮 OpenRouter AI Integration",
            font=("Segoe UI", 16, "bold"),
            text_color=self.colors.get('accent_primary', '#3CA0FF')
        )
        or_header.pack(pady=(10,5))
        
        disclaimer_text = (
            "💡 Tip: OpenRouter offers access to many AI models, including free ones!\n"
            "You can start with free models and explore others later.\n"
            "An API key is required to fetch model lists and use any model."
        )
        disclaimer_label = StandardLabel(
            openrouter_frame, text=disclaimer_text, font=("Segoe UI", 11),
            text_color=self.colors.get('text_secondary', '#d4d4d4'), justify="left",
            wraplength=openrouter_frame.winfo_width() - 40 if openrouter_frame.winfo_width() > 50 else 400
        )
        disclaimer_label.pack(pady=(0,10), padx=20, fill="x")
        
        # API Key Input Area
        api_key_input_frame = StandardFrame(openrouter_frame, fg_color="transparent")
        api_key_input_frame.pack(fill="x", padx=20, pady=(5,10))

        key_label = StandardLabel(api_key_input_frame, text="OpenRouter API Key (starts with 'sk-or-'):", font=("Segoe UI", 12))
        key_label.pack(side="left", padx=(0,5))
        
        self.api_key_entry = StandardEntry(
            api_key_input_frame, placeholder_text="sk-or-v1-...", width=300, show="*"
        )
        self.api_key_entry.pack(side="left", expand=True, fill="x", padx=5)
        # Pre-fill API key if already in wizard_data
        if self.wizard_data.get('openrouter_key'):
            self.api_key_entry.insert(0, self.wizard_data['openrouter_key'])

        # API Key Action Buttons (Get, Test)
        api_buttons_frame = StandardFrame(openrouter_frame, fg_color="transparent")
        api_buttons_frame.pack(fill="x", padx=20, pady=(0,10))

        get_key_btn = self.create_action_button(api_buttons_frame, "🔗 Get API Key", self._open_openrouter_keys_page, primary=False, width=150)
        get_key_btn.pack(side="left", padx=5)
        
        test_key_btn = self.create_action_button(api_buttons_frame, "🧪 Test & Save Key", self._test_and_save_api_key, primary=True, width=180)
        test_key_btn.pack(side="left", padx=5)

        # Model Selection Area
        model_selection_frame = StandardFrame(openrouter_frame, fg_color="transparent") # Changed to transparent
        model_selection_frame.pack(fill="x", padx=20, pady=10)
        
        model_label = StandardLabel(model_selection_frame, text="Default AI Model:", font=("Segoe UI", 12))
        model_label.pack(side="left", padx=(0,10))

        initial_models = ["meta-llama/llama-3.2-3b-instruct:free"] # Default if no key/fetch yet
        if self.wizard_data.get('openrouter_key') and self._fetched_models: # Use previously fetched if key matches
            initial_models = self._fetched_models
        elif self.wizard_data.get('ai_selected_model'): # Or if a model was saved from previous config
            initial_models = [self.wizard_data.get('ai_selected_model')] + [m for m in initial_models if m != self.wizard_data.get('ai_selected_model')]


        self.model_dropdown = StandardCombobox(
            model_selection_frame, values=initial_models, state="readonly", width=280
        )
        current_selected_model = self.wizard_data.get('ai_selected_model', initial_models[0] if initial_models else "")
        if current_selected_model in initial_models:
            self.model_dropdown.set(current_selected_model)
        elif initial_models:
            self.model_dropdown.set(initial_models[0])
        self.model_dropdown.pack(side="left", padx=5, expand=True, fill="x")

        fetch_models_btn = self.create_action_button(model_selection_frame, "🔄 Fetch Models", self._fetch_models_from_api, primary=False, width=150)
        fetch_models_btn.pack(side="left", padx=5)
        
        # Free/Premium Toggles (Simplified for now, can be expanded)
        # self.free_models_var = tk.BooleanVar(value=self.wizard_data.get('ai_free_models_only', True))
        # StandardSwitch(openrouter_frame, text="Use Only Free Models", variable=self.free_models_var).pack(pady=5)


        # Overall AI Status Indicator
        self.status_label = StandardLabel(
            ai_frame, text="Configure API key and select a model.", font=("Segoe UI", 12, "italic"),
            text_color=self.colors.get('text_muted', 'gray')
        )
        self.status_label.pack(pady=(10,0))
        self._update_ai_status_display() # Set initial status text

    def _open_openrouter_keys_page(self):
        webbrowser.open("https://openrouter.ai/keys")

    async def _validate_api_key_async(self, api_key: str) -> bool:
        """Asynchronously validates the API key with OpenRouter."""
        if not self.app or not self.app.ai_client: # ai_client might not be initialized if key is new
            # Temporarily create a client instance for validation if needed, or use a static method
            from ....ai.openrouter_client import OpenRouterClient # Local import
            temp_ai_client = OpenRouterClient(api_key=api_key, app_config=self.config, db_manager=None) # db_manager might not be needed for validation
            is_valid = await temp_ai_client.validate_api_key()
            # Important: Ensure temp_ai_client is properly closed if it opens sessions
            if hasattr(temp_ai_client, 'close_session'):
                 await temp_ai_client.close_session()
            return is_valid
        
        # If app.ai_client can be reconfigured or used for validation:
        # This assumes ai_client can have its key updated or can validate a new key.
        # current_key = self.app.ai_client.api_key
        # self.app.ai_client.api_key = api_key # Temporarily set for validation
        # is_valid = await self.app.ai_client.validate_api_key()
        # self.app.ai_client.api_key = current_key # Restore old key
        # return is_valid
        return False # Fallback if direct validation path not clear

    def _test_and_save_api_key(self):
        """Validates API key (simulated for now) and saves if valid."""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("API Key Missing", "Please enter your OpenRouter API key.", parent=self.wizard.window)
            return
        if not api_key.startswith("sk-or-"):
            messagebox.showwarning("Invalid Format", "OpenRouter API keys typically start with 'sk-or-'. Please check your key.", parent=self.wizard.window)
            # return # Allow user to proceed if they are sure, actual validation will fail if wrong

        # TODO: Replace with actual async validation
        # For now, we simulate success to allow UI flow.
        # In a real scenario:
        # self.wizard.show_loading_indicator() # Or similar
        # self.app.schedule_coroutine(self._process_key_validation(api_key))
        
        # --- Simulation ---
        self.wizard_data['openrouter_key'] = api_key
        self.wizard_data['ai_configured'] = True # Mark as configured once key is entered
        messagebox.showinfo("API Key Saved (Simulated Validation)", "API Key has been saved. Press 'Fetch Models' to update the model list.", parent=self.wizard.window)
        self._current_api_key_for_fetched_models = "" # Reset so fetch models uses new key
        self._update_ai_status_display()
        # --- End Simulation ---

    async def _process_key_validation(self, api_key: str):
        """Async helper to validate key and update UI."""
        is_valid = await self._validate_api_key_async(api_key)
        # self.wizard.hide_loading_indicator()
        if is_valid:
            self.wizard_data['openrouter_key'] = api_key
            self.wizard_data['ai_configured'] = True
            self._current_api_key_for_fetched_models = api_key # Store key used for fetch
            messagebox.showinfo("API Key Validated", "OpenRouter API Key is valid! You can now fetch models.", parent=self.wizard.window)
            await self._fetch_models_from_api_async(force_fetch=True) # Fetch models with new valid key
        else:
            self.wizard_data['openrouter_key'] = "" # Clear invalid key
            self.wizard_data['ai_configured'] = False
            messagebox.showerror("API Key Invalid", "The OpenRouter API Key provided is invalid or could not be verified.", parent=self.wizard.window)
        self._update_ai_status_display()


    async def _fetch_models_from_api_async(self, force_fetch: bool = False):
        """Asynchronously fetches models from OpenRouter API."""
        api_key = self.wizard_data.get('openrouter_key')
        if not api_key:
            messagebox.showwarning("API Key Required", "Please enter and save a valid OpenRouter API key first.", parent=self.wizard.window)
            return

        # Avoid re-fetching if key hasn't changed and we have models, unless forced
        if not force_fetch and self._fetched_models and self._current_api_key_for_fetched_models == api_key:
            self._update_model_dropdown(self._fetched_models)
            messagebox.showinfo("Models Loaded", "Model list loaded from cache for the current API key.", parent=self.wizard.window)
            return

        # self.wizard.show_loading_indicator()
        try:
            # Ensure ai_client is available and configured with the current key
            # This might mean re-initializing or updating the app's AI client
            if not self.app.ai_client or self.app.ai_client.api_key != api_key:
                 from ....ai.openrouter_client import OpenRouterClient # Local import
                 temp_ai_client = OpenRouterClient(api_key=api_key, app_config=self.config, db_manager=None)
                 models = await temp_ai_client.fetch_available_models()
                 if hasattr(temp_ai_client, 'close_session'): await temp_ai_client.close_session() # Clean up
            else: # Use existing app.ai_client
                models = await self.app.ai_client.fetch_available_models()

            if models:
                self._fetched_models = models
                self._current_api_key_for_fetched_models = api_key
                self._update_model_dropdown(models)
                messagebox.showinfo("Models Fetched", f"Successfully fetched {len(models)} models from OpenRouter.", parent=self.wizard.window)
            else:
                messagebox.showwarning("No Models Found", "Could not fetch models. The API key might be valid but have restrictions, or OpenRouter returned no models.", parent=self.wizard.window)
                self._fetched_models = [] # Clear cache on failure to fetch
        except Exception as e:
            messagebox.showerror("Fetch Error", f"Failed to fetch models: {e}", parent=self.wizard.window)
            self._fetched_models = [] # Clear cache on error
        finally:
            # self.wizard.hide_loading_indicator()
            self._update_ai_status_display()

    def _fetch_models_from_api(self):
        """Wrapper to schedule the async model fetching."""
        # This is a sync method called by a button. It needs to schedule the async task.
        # The wizard or app should have a way to run async tasks from sync UI events.
        # For simplicity, if event loop is running in another thread (common in Tkinter apps):
        if self.app and self.app.event_loop:
            asyncio.run_coroutine_threadsafe(self._fetch_models_from_api_async(), self.app.event_loop)
        else: # Fallback or direct call if in an async context (less common for Tkinter button commands)
            # This might block UI if not handled carefully.
            # Consider showing a "loading" message and disabling UI.
            # For now, direct async call for simplicity of example, assuming loop management exists.
            # This is NOT ideal for a real Tkinter app without proper async integration.
            try:
                # Ensure an event loop exists in the current context if not running in main thread
                # This part is tricky and depends heavily on the main app's threading model.
                # For now, we'll assume if self.app.event_loop is None, we might try to get/create one.
                # This is a simplification.
                loop = asyncio.get_event_loop_policy().get_event_loop() if not self.app.event_loop else self.app.event_loop
                if loop.is_running():
                    asyncio.ensure_future(self._fetch_models_from_api_async(), loop=loop)
                else:
                    loop.run_until_complete(self._fetch_models_from_api_async())
            except RuntimeError as e: # No event loop in current thread, or other policy issues
                 messagebox.showerror("Async Error", f"Event loop not configured to fetch models: {e}", parent=self.wizard.window)


    def _update_model_dropdown(self, models_data: List[Dict]): # Expect list of dicts from OpenRouterClient
        """Updates the model dropdown with the given list of models."""
        if not models_data:
            display_models = ["No models fetched - Check API Key"]
            self.wizard_data['available_ai_models'] = []
        else:
            # Extracting just the ID for display, but storing full data if needed later
            display_models = [model.get("id", "Unknown Model ID") for model in models_data]
            # Optionally store the full model data in wizard_data if other parts of app need it
            self.wizard_data['available_ai_models'] = models_data
        
        self.model_dropdown.configure(values=display_models)
        
        # Try to set to previously selected model, or first available, or default
        previously_selected_id = self.wizard_data.get('ai_selected_model')

        if previously_selected_id and previously_selected_id in display_models:
            self.model_dropdown.set(previously_selected_id)
        elif display_models and display_models[0] != "No models fetched - Check API Key":
            self.model_dropdown.set(display_models[0])
        else:
            self.model_dropdown.set(display_models[0] if display_models else "") # Set to the "No models..." or empty

        self._update_ai_status_display()


    def _update_ai_status_display(self):
        """Updates the status label based on configuration."""
        key_present = bool(self.wizard_data.get('openrouter_key'))
        model_selected_id = self.model_dropdown.get() if self.model_dropdown else self.wizard_data.get('ai_selected_model')
        is_placeholder_model = model_selected_id == "No models fetched - Check API Key" or not model_selected_id

        if key_present:
            if not is_placeholder_model:
                # Extracting only the model ID part before any potential colon (e.g., from "model/id:free")
                display_model_name = model_selected_id.split(':')[0]
                self.status_label.configure(
                    text=f"✅ Configured with model: {display_model_name}",
                    text_color=self.colors.get('success_color', 'green')
                )
            else: # Key is present, but model is placeholder or empty
                self.status_label.configure(
                    text="⚠️ API Key set. Please 'Fetch Models' and select one.",
                    text_color=self.colors.get('warning_color', 'orange')
                )
        else: # No API key
            self.status_label.configure(
                text="❌ AI Not Configured. Enter API key to enable.",
                text_color=self.colors.get('error_color', 'red')
            )
    
    def save_data(self):
        """Save AI configuration data to wizard_data."""
        # API key is typically saved by _test_and_save_api_key or its async counterpart.
        # However, ensure it's current from the entry if user typed and didn't "test & save".
        if self.api_key_entry:
             self.wizard_data['openrouter_key'] = self.api_key_entry.get().strip()

        if self.model_dropdown:
            selected_model_id = self.model_dropdown.get()
            # Avoid saving placeholder text as a model ID
            if selected_model_id and selected_model_id != "No models fetched - Check API Key":
                self.wizard_data['ai_selected_model'] = selected_model_id
            # If placeholder is selected, we might want to clear ai_selected_model or leave as is
            # depending on desired behavior. For now, only save actual model IDs.
            elif not selected_model_id or selected_model_id == "No models fetched - Check API Key":
                 if 'ai_selected_model' in self.wizard_data: # If a valid model was previously there
                      pass # Keep the old valid one if current is placeholder
                 else: # No previous valid model, and current is placeholder
                      self.wizard_data['ai_selected_model'] = ""


        # Update 'ai_configured' status based on presence of key AND a selected model (not placeholder)
        key_present = bool(self.wizard_data.get('openrouter_key'))
        model_validly_selected = bool(self.wizard_data.get('ai_selected_model') and \
                                   self.wizard_data.get('ai_selected_model') != "No models fetched - Check API Key")
        self.wizard_data['ai_configured'] = key_present and model_validly_selected

        # if self.free_models_var: # If this UI element is re-enabled
        #     self.wizard_data['ai_free_models_only'] = self.free_models_var.get()

        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            log_key_display = self.wizard_data.get('openrouter_key', "")[:10] + "..." if self.wizard_data.get('openrouter_key') else "None"
            logger.debug(f"AI Step save_data: Key='{log_key_display}', Model='{self.wizard_data.get('ai_selected_model')}', Configured={self.wizard_data['ai_configured']}")
        self._update_ai_status_display() # Refresh status after saving


    def validate(self) -> bool:
        """Validate AI step: if key is entered, a model should be selected."""
        # save_data() is called by the wizard before validate()
        api_key = self.wizard_data.get('openrouter_key', "").strip()
        selected_model_id = self.wizard_data.get('ai_selected_model', "").strip()
        is_placeholder_model = selected_model_id == "No models fetched - Check API Key" or not selected_model_id

        if api_key and is_placeholder_model:
            messagebox.showwarning(
                "Model Not Selected",
                "You've entered an API key for OpenRouter, but no valid AI model is selected.\n"
                "Please use 'Fetch Models' and choose a model from the list, or clear the API key if you don't want to configure AI now.",
                parent=self.wizard.window
            )
            return False

        # If no API key, it's fine (optional step).
        # If API key AND a valid model, it's fine.
        return True

    def can_skip(self) -> bool:
        return True # AI configuration is optional.
    
    def skip(self):
        """Handle skipping AI configuration."""
        self.wizard_data['skip_ai'] = True
        self.wizard_data['ai_configured'] = False
        self.wizard_data['openrouter_key'] = '' # Clear any entered key
        self.wizard_data['ai_selected_model'] = '' # Clear selected model
        logger = getattr(self.wizard, 'logger', self.app.logger if self.app else None)
        if logger:
            logger.info("AI services step skipped.")
