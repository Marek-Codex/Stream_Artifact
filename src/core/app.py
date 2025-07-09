"""
Core Application Module for Stream Artifact
Handles the main application lifecycle and coordination
"""

import asyncio
import threading
import logging
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from rich.console import Console
from rich.logging import RichHandler

from ..ui.main_window import MainWindow
from ..core.config import Config
from ..core.database import Database
from ..core.twitch_client import TwitchClient
from ..ai.openrouter_client import OpenRouterClient

# Configure rich console
console = Console()

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)


class StreamArtifact:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        self.config = Config()
        self.database = Database()
        self.twitch_client: Optional[TwitchClient] = None
        self.ai_client: Optional[OpenRouterClient] = None
        self.main_window: Optional[MainWindow] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.loop_thread: Optional[threading.Thread] = None
        
        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        logger.info("🌟 Stream Artifact initialized")
    
    def run(self):
        """Run the main application"""
        try:
            # Start the async event loop in a separate thread
            self.start_event_loop()
            
            # Create and run the main GUI
            self.main_window = MainWindow(self)
            self.main_window.run()
            
        except Exception as e:
            logger.error(f"❌ Application error: {e}")
            raise
        finally:
            self.cleanup()
    
    def start_event_loop(self):
        """Start the asyncio event loop in a separate thread"""
        def run_loop():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        logger.info("🔄 Event loop started")
    
    def cleanup(self):
        """Clean up resources"""
        if self.event_loop and not self.event_loop.is_closed():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        
        if self.twitch_client:
            # Stop Twitch client
            pass
        
        logger.info("🧹 Cleanup completed")
    
    async def connect_twitch(self, channel: str, token: str):
        """Connect to Twitch chat"""
        try:
            self.twitch_client = TwitchClient(channel, token, self.ai_client, self.database)
            await self.twitch_client.connect()
            logger.info(f"🎮 Connected to Twitch: {channel}")
        except Exception as e:
            logger.error(f"❌ Twitch connection failed: {e}")
            raise
    
    def initialize_ai(self, api_key: str, model: str):
        """Initialize AI client"""
        try:
            self.ai_client = OpenRouterClient(api_key, model, self.database, self.config)
            logger.info(f"🤖 AI client initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ AI initialization failed: {e}", exc_info=True) # Add exc_info for better debugging
            raise
    
    def schedule_coroutine(self, coro):
        """Schedule a coroutine to run in the event loop"""
        if self.event_loop and not self.event_loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
            return future
        else:
            logger.error("❌ Event loop not available or closed when trying to schedule coroutine.")
            return None

    # Removed duplicate initialize_ai and schedule_coroutine methods.
    # The first versions were kept. The second initialize_ai was missing self.config pass.
    # The first schedule_coroutine was slightly more robust with the is_closed check.

    async def initialize_clients_from_config(self):
        """
        Initialize AI and Twitch clients based on the current configuration.
        This can be called after setup or when settings change.
        """
        logger.info("Attempting to initialize clients from configuration...")

        # Initialize AI Client
        openrouter_api_key = self.config.get('ai', 'openrouter_api_key')
        selected_model = self.config.get('ai', 'selected_model')

        if openrouter_api_key and selected_model:
            try:
                # Use the existing initialize_ai method which handles instantiation
                self.initialize_ai(openrouter_api_key, selected_model) # This is synchronous
                logger.info(f"AI Client re-initialized with model: {selected_model}")
                if self.main_window: # Update UI if main window exists
                    self.main_window.post_activity_log(f"AI Client initialized: {selected_model}")
            except Exception as e:
                logger.error(f"Failed to initialize AI client from config: {e}", exc_info=True)
                if self.main_window:
                    self.main_window.post_activity_log(f"Error initializing AI: {e}")
        else:
            logger.info("AI client not configured (missing API key or model in config).")
            self.ai_client = None # Ensure it's None if not configured

        # Update Twitch client if AI client has changed (as it's a dependency)
        if self.twitch_client and self.twitch_client.ai_client != self.ai_client:
            logger.info("AI client instance changed, updating Twitch client.")
            self.twitch_client.ai_client = self.ai_client
            if self.main_window:
                 self.main_window.post_activity_log("Twitch client updated with new AI client instance.")

        # Note: Twitch client connection itself is typically user-initiated via UI after setup.
        # This method primarily ensures the client *instances* are ready based on config.
        # Auto-connecting Twitch could be a separate method or part of `connect_services`.


    async def connect_services(self):
        """Connect all configured services, e.g., Twitch."""
        logger.info("Attempting to connect services...")
        # For now, only Twitch. This can be expanded.
        twitch_channel = self.config.get('twitch', 'broadcaster_username')
        # Determine which token to use: bot token if available and not using broadcaster as bot, else broadcaster token
        use_broadcaster_as_bot = self.config.get_bool('twitch', 'use_broadcaster_as_bot', True)
        bot_token = self.config.get('twitch', 'bot_token')
        broadcaster_token = self.config.get('twitch', 'broadcaster_token')

        twitch_token_to_use = None
        if not use_broadcaster_as_bot and bot_token:
            twitch_token_to_use = bot_token
            logger.info("Using separate bot account token for Twitch connection.")
        elif broadcaster_token:
            twitch_token_to_use = broadcaster_token
            logger.info("Using broadcaster account token for Twitch connection.")
        else:
            logger.error("No valid Twitch token found for connection.")
            if self.main_window:
                self.main_window.update_connection_ui(False, "Twitch token missing")
                self.main_window.post_activity_log("❌ Twitch connection failed: Token missing.")
            return

        if twitch_channel and twitch_token_to_use:
            # Ensure AI client is initialized before Twitch client might need it
            if not self.ai_client and self.config.get('ai', 'openrouter_api_key') and self.config.get('ai', 'selected_model'):
                 self.initialize_ai(self.config.get('ai', 'openrouter_api_key'), self.config.get('ai', 'selected_model'))

            try:
                # Pass the correct config for channel (usually broadcaster's channel)
                # and the token determined above.
                # The TwitchClient needs to know which username corresponds to the token for sending messages.
                # This might need refinement in TwitchClient or here.

                # For now, assume TwitchClient uses the token to identify itself.
                # The 'channel' parameter is the channel to join.
                await self.connect_twitch(channel=f"#{twitch_channel.lower()}", token=twitch_token_to_use)

                if self.main_window:
                    self.main_window.update_connection_ui(True, f"Connected to Twitch: #{twitch_channel}")
                    self.main_window.post_activity_log(f"🎮 Connected to Twitch: #{twitch_channel}")

            except Exception as e:
                logger.error(f"Error connecting Twitch: {e}", exc_info=True)
                if self.main_window:
                    self.main_window.update_connection_ui(False, f"Twitch Error: {e}")
                    self.main_window.post_activity_log(f"❌ Twitch connection error: {e}")
        else:
            logger.warning("Twitch channel or token not configured. Cannot connect.")
            if self.main_window:
                self.main_window.update_connection_ui(False, "Twitch not configured")
                self.main_window.post_activity_log("ℹ️ Twitch not configured. Cannot connect.")


    async def disconnect_services(self):
        """Disconnect all connected services."""
        logger.info("Disconnecting services...")
        if self.twitch_client and self.twitch_client.is_connected(): # Assuming is_connected method
            try:
                await self.twitch_client.close_connection() # Assuming close_connection method
                logger.info("🔌 Twitch client disconnected.")
                if self.main_window:
                    self.main_window.update_connection_ui(False, "Disconnected from Twitch")
                    self.main_window.post_activity_log("🔌 Disconnected from Twitch.")
            except Exception as e:
                logger.error(f"Error disconnecting Twitch: {e}", exc_info=True)
                if self.main_window:
                     self.main_window.post_activity_log(f"❌ Error disconnecting Twitch: {e}")
        self.twitch_client = None # Clear the client instance after disconnecting

        # Could add AI client cleanup if it holds resources, e.g., session
        if self.ai_client and hasattr(self.ai_client, 'close'):
            await self.ai_client.close()
            logger.info("🤖 AI client session closed.")
        # self.ai_client = None # Optionally clear AI client too, or re-init on next connect

    def toggle_connection_services(self):
        """Toggles the connection state of services."""
        # This method is synchronous and called from UI. It schedules async connect/disconnect.
        if self.twitch_client and self.twitch_client.is_connected(): # Check a reliable connection status
            logger.info("Toggle: Currently connected, scheduling disconnect.")
            self.schedule_coroutine(self.disconnect_services())
        else:
            logger.info("Toggle: Currently disconnected, scheduling connect.")
            self.schedule_coroutine(self.connect_services())

    def on_close(self):
        """Handle application close sequence."""
        logger.info("Application on_close triggered.")
        # Perform cleanup, ensure async tasks are handled, then destroy UI
        if self.main_window: # Ensure main_window exists
            # Potentially save window geometry or other states here via self.config
            # e.g., self.config.set('ui', 'window_geometry', self.main_window.root.geometry())
            # self.config.save()
            pass

        # Schedule disconnection of services if any are active
        # Check a reliable connection status before attempting disconnect
        is_connected_somehow = self.twitch_client and self.twitch_client.is_connected() # Example

        if is_connected_somehow:
            logger.info("Services seem connected, attempting graceful disconnect.")
            # Schedule disconnection and wait for it if possible, or just schedule and proceed
            # This is tricky with a daemon thread for the event loop.
            # For now, just schedule it. The cleanup in run() will also try to stop the loop.
            self.schedule_coroutine(self.disconnect_services())
            # Give a moment for scheduled tasks to potentially run, though not guaranteed
            # if the main loop is about to exit from main_window.destroy().
            # A more robust solution might involve joining the loop_thread after main_window.destroy()
            # and ensuring the loop has processed shutdown tasks.

        # Proceed to destroy the UI - this will end the mainloop in main_window.run()
        if self.main_window:
            self.main_window.destroy()

        # The finally block in self.run() will call self.cleanup() which stops the event loop.
        logger.info("Application close sequence initiated. UI destruction will follow.")
