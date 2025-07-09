"""
Database Management for Stream Artifact
Handles SQLite database operations for user data, messages, and memory
"""

import aiosqlite
import sqlite3
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database manager for Stream Artifact"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default path in user's home directory
            config_dir = Path.home() / ".stream_artifact"
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / "stream_artifact.db"
        
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            # Use synchronous connection for initialization
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    user_id TEXT UNIQUE,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    is_subscriber BOOLEAN DEFAULT FALSE,
                    is_vip BOOLEAN DEFAULT FALSE,
                    is_moderator BOOLEAN DEFAULT FALSE,
                    is_regular BOOLEAN DEFAULT FALSE,
                    points INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Messages table for chat history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    channel TEXT NOT NULL,
                    message_type TEXT DEFAULT 'chat',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # AI Memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    context TEXT NOT NULL,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    relevance_score REAL DEFAULT 1.0,
                    memory_type TEXT DEFAULT 'conversation',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Commands table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT UNIQUE NOT NULL,
                    response TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    permission_level TEXT DEFAULT 'everyone',
                    cooldown INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Stream events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stream_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    username TEXT,
                    data TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Topics table for conversation tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    related_users TEXT DEFAULT '[]',
                    sentiment REAL DEFAULT 0.0
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_username ON messages(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_memory_username ON ai_memory(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_memory_timestamp ON ai_memory(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stream_events_timestamp ON stream_events(timestamp)")
            
            conn.commit()
            conn.close()
            
            logger.info("🗄️ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def connect(self):
        """Connect to the database (async)"""
        if self.connection is None:
            self.connection = await aiosqlite.connect(str(self.db_path))
            self.connection.row_factory = aiosqlite.Row
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self.connection:
            await self.connection.close()
            self.connection = None
    
    async def add_user(self, username: str, display_name: str = None, user_id: str = None,
                      is_subscriber: bool = False, is_vip: bool = False, is_moderator: bool = False) -> None:
        """Add or update a user in the database"""
        await self.connect()
        
        try:
            await self.connection.execute("""
                INSERT OR REPLACE INTO users 
                (username, display_name, user_id, last_seen, is_subscriber, is_vip, is_moderator)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
            """, (username, display_name or username, user_id, is_subscriber, is_vip, is_moderator))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to add user {username}: {e}")
    
    async def add_message(self, username: str, content: str, channel: str, 
                         message_type: str = 'chat', metadata: Dict = None) -> None:
        """Add a message to the database"""
        await self.connect()
        
        try:
            metadata_json = json.dumps(metadata or {})
            
            await self.connection.execute("""
                INSERT INTO messages (username, content, channel, message_type, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (username, content, channel, message_type, metadata_json))
            
            # Update user message count
            await self.connection.execute("""
                UPDATE users SET message_count = message_count + 1, last_seen = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (username,))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to add message from {username}: {e}")
    
    async def add_ai_memory(self, username: str, context: str, response: str = None,
                           relevance_score: float = 1.0, memory_type: str = 'conversation',
                           metadata: Dict = None) -> None:
        """Add AI memory/context to the database"""
        await self.connect()
        
        try:
            metadata_json = json.dumps(metadata or {})
            
            await self.connection.execute("""
                INSERT INTO ai_memory (username, context, response, relevance_score, memory_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, context, response, relevance_score, memory_type, metadata_json))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to add AI memory for {username}: {e}")
    
    async def get_recent_messages(self, channel: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a channel"""
        await self.connect()
        
        try:
            cursor = await self.connection.execute("""
                SELECT username, content, timestamp, message_type, metadata
                FROM messages
                WHERE channel = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (channel, limit))
            
            rows = await cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append({
                    'username': row['username'],
                    'content': row['content'],
                    'timestamp': row['timestamp'],
                    'message_type': row['message_type'],
                    'metadata': json.loads(row['metadata'] or '{}')
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent messages: {e}")
            return []
    
    async def get_user_memory(self, username: str, limit: int = 10) -> List[Dict]:
        """Get AI memory for a specific user"""
        await self.connect()
        
        try:
            cursor = await self.connection.execute("""
                SELECT context, response, timestamp, relevance_score, memory_type, metadata
                FROM ai_memory
                WHERE username = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (username, limit))
            
            rows = await cursor.fetchall()
            
            memory = []
            for row in rows:
                memory.append({
                    'context': row['context'],
                    'response': row['response'],
                    'timestamp': row['timestamp'],
                    'relevance_score': row['relevance_score'],
                    'memory_type': row['memory_type'],
                    'metadata': json.loads(row['metadata'] or '{}')
                })
            
            return memory
            
        except Exception as e:
            logger.error(f"❌ Failed to get user memory for {username}: {e}")
            return []
    
    async def get_user_stats(self, username: str) -> Optional[Dict]:
        """Get statistics for a user"""
        await self.connect()
        
        try:
            cursor = await self.connection.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            
            row = await cursor.fetchone()
            
            if row:
                return {
                    'username': row['username'],
                    'display_name': row['display_name'],
                    'first_seen': row['first_seen'],
                    'last_seen': row['last_seen'],
                    'message_count': row['message_count'],
                    'is_subscriber': row['is_subscriber'],
                    'is_vip': row['is_vip'],
                    'is_moderator': row['is_moderator'],
                    'is_regular': row['is_regular'],
                    'points': row['points'],
                    'metadata': json.loads(row['metadata'] or '{}')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats for {username}: {e}")
            return None
    
    async def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old data from the database"""
        await self.connect()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Clean old messages
            await self.connection.execute("""
                DELETE FROM messages WHERE timestamp < ?
            """, (cutoff_date,))
            
            # Clean old AI memory with low relevance
            await self.connection.execute("""
                DELETE FROM ai_memory 
                WHERE timestamp < ? AND relevance_score < 0.3
            """, (cutoff_date,))
            
            await self.connection.commit()
            
            logger.info(f"🧹 Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")
    
    async def add_stream_event(self, event_type: str, username: str = None, data: Dict = None) -> None:
        """Add a stream event to the database"""
        await self.connect()
        
        try:
            data_json = json.dumps(data or {})
            
            await self.connection.execute("""
                INSERT INTO stream_events (event_type, username, data)
                VALUES (?, ?, ?)
            """, (event_type, username, data_json))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to add stream event {event_type}: {e}")
    
    async def get_recent_events(self, limit: int = 25) -> List[Dict]:
        """Get recent stream events"""
        await self.connect()
        
        try:
            cursor = await self.connection.execute("""
                SELECT event_type, username, data, timestamp
                FROM stream_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = await cursor.fetchall()
            
            events = []
            for row in rows:
                events.append({
                    'event_type': row['event_type'],
                    'username': row['username'],
                    'data': json.loads(row['data'] or '{}'),
                    'timestamp': row['timestamp']
                })
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent events: {e}")
            return []
