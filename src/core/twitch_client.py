"""
Twitch Client for Stream Artifact
Handles Twitch chat connection and message processing
"""

import asyncio
import random
import logging
from typing import Optional, Dict, List, Callable
from datetime import datetime, timedelta

import twitchio
from twitchio.ext import commands

logger = logging.getLogger(__name__)


class TwitchClient(commands.Bot):
    """Enhanced Twitch bot client with AI integration"""
    
    def __init__(self, channel: str, token: str, ai_client, database=None):
        # Initialize the bot
        super().__init__(
            token=token,
            prefix='!',
            initial_channels=[channel]
        )
        
        self.target_channel = channel
        self.ai_client = ai_client
        self.database = database
        self.is_connected = False
        self.message_queue = asyncio.Queue()
        self.last_ai_response = datetime.now() - timedelta(seconds=30)
        
        # Command cooldowns
        self.command_cooldowns: Dict[str, datetime] = {}
        self.user_cooldowns: Dict[str, datetime] = {}
        
        # Chat statistics
        self.stats = {
            'messages_received': 0,
            'ai_responses_sent': 0,
            'commands_processed': 0,
            'uptime': datetime.now()
        }
        
        logger.info(f"🤖 Twitch client initialized for channel: {channel}")
    
    async def event_ready(self):
        """Called when the bot is ready"""
        self.is_connected = True
        logger.info(f"🎮 Connected to Twitch as {self.nick}")
        logger.info(f"📺 Joining channel: {self.target_channel}")
    
    async def event_message(self, message):
        """Handle incoming messages"""
        # Skip messages from the bot itself
        if message.echo:
            return
        
        # Update statistics
        self.stats['messages_received'] += 1
        
        # Store message in database
        if self.database:
            await self.database.add_message(
                username=message.author.name,
                content=message.content,
                channel=message.channel.name,
                message_type='chat',
                metadata={
                    'display_name': message.author.display_name,
                    'is_subscriber': message.author.is_subscriber,
                    'is_vip': message.author.is_vip,
                    'is_mod': message.author.is_mod,
                    'badges': [badge.name for badge in message.author.badges] if message.author.badges else []
                }
            )
        
        # Update user info
        if self.database:
            await self.database.add_user(
                username=message.author.name,
                display_name=message.author.display_name,
                user_id=str(message.author.id),
                is_subscriber=message.author.is_subscriber,
                is_vip=message.author.is_vip,
                is_moderator=message.author.is_mod
            )
        
        # Handle commands
        if message.content.startswith('!'):
            await self.handle_command(message)
        else:
            # Check for AI response opportunity
            await self.check_ai_response(message)
    
    async def handle_command(self, message):
        """Handle bot commands"""
        command = message.content.lower().split()[0][1:]  # Remove '!' prefix
        
        # Check cooldowns
        if not self.check_cooldown(command, message.author.name):
            return
        
        self.stats['commands_processed'] += 1
        
        # AI-related commands
        if command in ['ai', 'ask', 'question']:
            await self.handle_ai_command(message)
        elif command == 'help':
            await self.handle_help_command(message)
        elif command == 'stats':
            await self.handle_stats_command(message)
        elif command == 'uptime':
            await self.handle_uptime_command(message)
        
        # Process through commands extension
        await self.handle_commands(message)
    
    async def handle_ai_command(self, message):
        """Handle AI chat commands"""
        try:
            # Extract the question/prompt
            parts = message.content.split(' ', 1)
            prompt = parts[1] if len(parts) > 1 else "Hello! How can I help you?"
            
            # Get AI response
            if self.ai_client:
                response = await self.ai_client.get_response(
                    prompt=prompt,
                    username=message.author.name,
                    context={
                        'channel': message.channel.name,
                        'is_command': True,
                        'display_name': message.author.display_name,
                        'is_subscriber': message.author.is_subscriber,
                        'is_vip': message.author.is_vip,
                        'is_mod': message.author.is_mod
                    }
                )
                
                if response:
                    await message.channel.send(f"@{message.author.display_name} {response}")
                    self.stats['ai_responses_sent'] += 1
                else:
                    await message.channel.send(f"@{message.author.display_name} Sorry, I'm having trouble thinking right now! 🤔")
            else:
                await message.channel.send(f"@{message.author.display_name} AI is not available right now!")
                
        except Exception as e:
            logger.error(f"❌ Error handling AI command: {e}")
            await message.channel.send(f"@{message.author.display_name} Oops! Something went wrong! 😅")
    
    async def handle_help_command(self, message):
        """Handle help command"""
        help_text = "🤖 Available commands: !ai <question>, !help, !stats, !uptime | I also respond naturally to chat!"
        await message.channel.send(help_text)
    
    async def handle_stats_command(self, message):
        """Handle stats command"""
        uptime = datetime.now() - self.stats['uptime']
        stats_text = f"📊 Messages: {self.stats['messages_received']} | AI Responses: {self.stats['ai_responses_sent']} | Commands: {self.stats['commands_processed']} | Uptime: {self.format_duration(uptime)}"
        await message.channel.send(stats_text)
    
    async def handle_uptime_command(self, message):
        """Handle uptime command"""
        uptime = datetime.now() - self.stats['uptime']
        await message.channel.send(f"⏱️ Bot uptime: {self.format_duration(uptime)}")
    
    async def check_ai_response(self, message):
        """Check if bot should respond to regular chat"""
        try:
            # Skip if AI client is not available
            if not self.ai_client:
                return
            
            # Get AI configuration
            ai_config = self.ai_client.config.ai if hasattr(self.ai_client, 'config') else None
            if not ai_config:
                return
            
            # Check if random responses are enabled
            if not hasattr(ai_config, 'random_reply_chance') or ai_config.random_reply_chance <= 0:
                return
            
            # Check cooldown (prevent spam)
            if datetime.now() - self.last_ai_response < timedelta(seconds=30):
                return
            
            # Random chance to respond
            if random.random() < ai_config.random_reply_chance:
                response = await self.ai_client.get_response(
                    prompt=message.content,
                    username=message.author.name,
                    context={
                        'channel': message.channel.name,
                        'is_command': False,
                        'is_random_reply': True,
                        'display_name': message.author.display_name,
                        'is_subscriber': message.author.is_subscriber,
                        'is_vip': message.author.is_vip,
                        'is_mod': message.author.is_mod
                    }
                )
                
                if response:
                    await message.channel.send(response)
                    self.stats['ai_responses_sent'] += 1
                    self.last_ai_response = datetime.now()
                    
        except Exception as e:
            logger.error(f"❌ Error checking AI response: {e}")
    
    def check_cooldown(self, command: str, username: str, cooldown_seconds: int = 5) -> bool:
        """Check if command/user is on cooldown"""
        now = datetime.now()
        
        # Check command cooldown
        if command in self.command_cooldowns:
            if now - self.command_cooldowns[command] < timedelta(seconds=cooldown_seconds):
                return False
        
        # Check user cooldown
        user_key = f"{username}_{command}"
        if user_key in self.user_cooldowns:
            if now - self.user_cooldowns[user_key] < timedelta(seconds=cooldown_seconds):
                return False
        
        # Update cooldowns
        self.command_cooldowns[command] = now
        self.user_cooldowns[user_key] = now
        
        return True
    
    def format_duration(self, duration: timedelta) -> str:
        """Format duration for display"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    async def send_message(self, message: str, channel: str = None):
        """Send a message to chat"""
        try:
            target_channel = channel or self.target_channel
            channel_obj = self.get_channel(target_channel)
            
            if channel_obj:
                await channel_obj.send(message)
                logger.info(f"📤 Sent message to {target_channel}: {message}")
            else:
                logger.error(f"❌ Channel {target_channel} not found")
                
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
    
    async def connect(self):
        """Connect to Twitch"""
        try:
            await self.start()
        except Exception as e:
            logger.error(f"❌ Failed to connect to Twitch: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Twitch"""
        try:
            await self.close()
            self.is_connected = False
            logger.info("🔌 Disconnected from Twitch")
        except Exception as e:
            logger.error(f"❌ Error disconnecting: {e}")
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        uptime = datetime.now() - self.stats['uptime']
        return {
            **self.stats,
            'uptime_formatted': self.format_duration(uptime),
            'is_connected': self.is_connected
        }
