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
            logger.error(f"❌ AI initialization failed: {e}")
            raise
    
    def schedule_coroutine(self, coro):
        """Schedule a coroutine to run in the event loop"""
        if self.event_loop and not self.event_loop.is_closed():
            return asyncio.run_coroutine_threadsafe(coro, self.event_loop)
        return None
    
    def initialize_ai(self, api_key: str, model: str):
        """Initialize the AI client"""
        try:
            self.ai_client = OpenRouterClient(api_key, model, self.database)
            logger.info(f"🤖 AI client initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ AI initialization failed: {e}")
            raise
    
    def schedule_coroutine(self, coro):
        """Schedule a coroutine to run in the event loop"""
        if self.event_loop:
            future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
            return future
        else:
            logger.error("❌ Event loop not available")
            return None
