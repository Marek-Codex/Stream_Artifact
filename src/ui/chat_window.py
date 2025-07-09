"""
Chat Window for Stream Artifact
Displays live chat with cyberpunk styling
"""

import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
from datetime import datetime
from typing import Dict, List, Optional
import re
import logging

from .components.cyberpunk_widgets import CyberpunkFrame, CyberpunkTextbox, CyberpunkEntry, CyberpunkButton, CyberpunkLabel

logger = logging.getLogger(__name__)


class ChatWindow:
    """Chat window with cyberpunk styling and real-time updates"""
    
    def __init__(self, parent, colors: Dict[str, str]):
        self.parent = parent
        self.colors = colors
        self.chat_frame = None
        self.chat_display = None
        self.input_frame = None
        self.message_input = None
        self.send_button = None
        
        # Chat state
        self.messages = []
        self.max_messages = 1000
        self.auto_scroll = True
        
        # Text formatting
        self.username_colors = [
            "#00d4ff", "#ff00ff", "#00ff41", "#ffaa00", 
            "#ff4444", "#4444ff", "#ff8800", "#8800ff"
        ]
        self.color_index = 0
        self.user_colors = {}
        
        logger.info("💬 Chat window initialized")
    
    def create_interface(self):
        """Create the chat interface"""
        # Main chat frame
        self.chat_frame = CyberpunkFrame(
            self.parent,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chat header
        self._create_header()
        
        # Chat display area
        self._create_chat_display()
        
        # Message input area
        self._create_input_area()
        
        # Add some example messages
        self._add_example_messages()
    
    def _create_header(self):
        """Create the chat header"""
        header_frame = CyberpunkFrame(
            self.chat_frame,
            height=40,
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['accent_primary'],
            border_width=1
        )
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = CyberpunkLabel(
            header_frame,
            text="💬 LIVE CHAT",
            font=("Consolas", 14, "bold"),
            text_color=self.colors['accent_primary']
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ctk.CTkCheckBox(
            header_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self._toggle_auto_scroll,
            text_color=self.colors['text_secondary'],
            font=("Consolas", 10),
            fg_color=self.colors['accent_primary'],
            hover_color=self.colors['hover_color']
        )
        auto_scroll_check.pack(side="right", padx=10, pady=10)
        
        # Clear button
        clear_button = CyberpunkButton(
            header_frame,
            text="🗑️ Clear",
            command=self._clear_chat,
            width=80,
            height=30,
            fg_color=self.colors['bg_primary'],
            hover_color=self.colors['hover_color'],
            border_color=self.colors['error_color']
        )
        clear_button.pack(side="right", padx=5, pady=5)
    
    def _create_chat_display(self):
        """Create the chat display area"""
        # Chat display frame
        display_frame = CyberpunkFrame(
            self.chat_frame,
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        display_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create text widget for chat
        self.chat_display = tk.Text(
            display_frame,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            border=0,
            relief="flat",
            selectbackground=self.colors['accent_primary'],
            selectforeground=self.colors['bg_primary']
        )
        
        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(
            display_frame,
            command=self.chat_display.yview,
            fg_color=self.colors['bg_secondary'],
            button_color=self.colors['accent_primary'],
            button_hover_color=self.colors['hover_color']
        )
        
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        scrollbar.pack(side="right", fill="y")
        self.chat_display.pack(side="left", fill="both", expand=True)
        
        # Configure text tags for styling
        self._setup_text_tags()
        
        # Bind scroll events
        self.chat_display.bind("<Button-1>", self._on_click)
        self.chat_display.bind("<MouseWheel>", self._on_scroll)
    
    def _create_input_area(self):
        """Create the message input area"""
        self.input_frame = CyberpunkFrame(
            self.chat_frame,
            height=60,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['border_color'],
            border_width=1
        )
        self.input_frame.pack(fill="x", padx=5, pady=5)
        self.input_frame.pack_propagate(False)
        
        # Message input
        self.message_input = CyberpunkEntry(
            self.input_frame,
            placeholder_text="Type a message to send to chat...",
            fg_color=self.colors['bg_primary'],
            border_color=self.colors['border_color'],
            text_color=self.colors['text_primary'],
            font=("Consolas", 11)
        )
        self.message_input.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Send button
        self.send_button = CyberpunkButton(
            self.input_frame,
            text="📤 Send",
            command=self._send_message,
            width=80,
            height=40,
            fg_color=self.colors['accent_primary'],
            hover_color=self.colors['hover_color'],
            text_color=self.colors['bg_primary']
        )
        self.send_button.pack(side="right", padx=10, pady=10)
        
        # Bind Enter key
        self.message_input.bind("<Return>", lambda e: self._send_message())
    
    def _setup_text_tags(self):
        """Set up text tags for message styling"""
        # Username tags with different colors
        for i, color in enumerate(self.username_colors):
            self.chat_display.tag_configure(f"username_{i}", foreground=color, font=("Consolas", 10, "bold"))
        
        # Message type tags
        self.chat_display.tag_configure("timestamp", foreground=self.colors['text_secondary'], font=("Consolas", 8))
        self.chat_display.tag_configure("system", foreground=self.colors['warning_color'], font=("Consolas", 10, "italic"))
        self.chat_display.tag_configure("ai_response", foreground=self.colors['accent_tertiary'], font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("command", foreground=self.colors['accent_secondary'], font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("subscriber", foreground=self.colors['accent_primary'])
        self.chat_display.tag_configure("vip", foreground=self.colors['warning_color'])
        self.chat_display.tag_configure("moderator", foreground=self.colors['success_color'])
        
        # URL/link tags
        self.chat_display.tag_configure("url", foreground=self.colors['accent_primary'], underline=True)
        self.chat_display.tag_bind("url", "<Button-1>", self._open_url)
        self.chat_display.tag_bind("url", "<Enter>", lambda e: self.chat_display.configure(cursor="hand2"))
        self.chat_display.tag_bind("url", "<Leave>", lambda e: self.chat_display.configure(cursor=""))
    
    def _toggle_auto_scroll(self):
        """Toggle auto-scroll functionality"""
        self.auto_scroll = self.auto_scroll_var.get()
        logger.info(f"Auto-scroll {'enabled' if self.auto_scroll else 'disabled'}")
    
    def _clear_chat(self):
        """Clear the chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state=tk.DISABLED)
        self.messages.clear()
        logger.info("Chat cleared")
    
    def _send_message(self):
        """Send a message (placeholder for bot testing)"""
        message = self.message_input.get().strip()
        if message:
            # Clear input
            self.message_input.delete(0, tk.END)
            
            # Add as system message for testing
            self.add_message("StreamArtifact", f"[TEST] {message}", message_type="system")
            
            logger.info(f"Test message sent: {message}")
    
    def _on_click(self, event):
        """Handle clicks in chat display"""
        # Disable auto-scroll temporarily when user clicks
        self.auto_scroll = False
        self.auto_scroll_var.set(False)
    
    def _on_scroll(self, event):
        """Handle scroll events"""
        # Check if user scrolled to bottom
        if self.chat_display.yview()[1] >= 0.98:
            self.auto_scroll = True
            self.auto_scroll_var.set(True)
        else:
            self.auto_scroll = False
            self.auto_scroll_var.set(False)
    
    def _open_url(self, event):
        """Open URL in browser"""
        # Get the URL from the clicked text
        index = self.chat_display.index(tk.CURRENT)
        line_start = self.chat_display.index(f"{index} linestart")
        line_end = self.chat_display.index(f"{index} lineend")
        line_text = self.chat_display.get(line_start, line_end)
        
        # Extract URL (simplified)
        import webbrowser
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line_text)
        if urls:
            webbrowser.open(urls[0])
    
    def add_message(self, username: str, message: str, timestamp: str = None, message_type: str = "chat", user_badges: List[str] = None):
        """Add a message to the chat display"""
        try:
            # Create timestamp if not provided
            if timestamp is None:
                timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Assign color to user if not already assigned
            if username not in self.user_colors:
                self.user_colors[username] = self.color_index % len(self.username_colors)
                self.color_index += 1
            
            color_index = self.user_colors[username]
            
            # Enable text widget for editing
            self.chat_display.configure(state=tk.NORMAL)
            
            # Insert timestamp
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Insert username with styling
            username_tag = f"username_{color_index}"
            
            # Add badges
            if user_badges:
                badge_text = ""
                for badge in user_badges:
                    if badge == "subscriber":
                        badge_text += "⭐"
                    elif badge == "vip":
                        badge_text += "💎"
                    elif badge == "moderator":
                        badge_text += "🔨"
                
                if badge_text:
                    self.chat_display.insert(tk.END, f"{badge_text} ", "system")
            
            # Insert username
            self.chat_display.insert(tk.END, f"{username}: ", username_tag)
            
            # Insert message with appropriate styling
            if message_type == "system":
                self.chat_display.insert(tk.END, f"{message}\n", "system")
            elif message_type == "ai_response":
                self.chat_display.insert(tk.END, f"{message}\n", "ai_response")
            elif message_type == "command":
                self.chat_display.insert(tk.END, f"{message}\n", "command")
            else:
                # Regular message - check for URLs
                self._insert_message_with_urls(message)
            
            # Disable text widget
            self.chat_display.configure(state=tk.DISABLED)
            
            # Auto-scroll if enabled
            if self.auto_scroll:
                self.chat_display.see(tk.END)
            
            # Store message
            self.messages.append({
                'username': username,
                'message': message,
                'timestamp': timestamp,
                'type': message_type,
                'badges': user_badges or []
            })
            
            # Limit message history
            if len(self.messages) > self.max_messages:
                self.messages.pop(0)
                # Clear some old messages from display
                self._cleanup_old_messages()
            
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
    
    def _insert_message_with_urls(self, message: str):
        """Insert message with URL highlighting"""
        # Find URLs in the message
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.finditer(url_pattern, message)
        
        last_end = 0
        for match in urls:
            # Insert text before URL
            self.chat_display.insert(tk.END, message[last_end:match.start()])
            
            # Insert URL with special tag
            self.chat_display.insert(tk.END, match.group(), "url")
            
            last_end = match.end()
        
        # Insert remaining text
        self.chat_display.insert(tk.END, message[last_end:] + "\n")
    
    def _cleanup_old_messages(self):
        """Clean up old messages from display"""
        # Get current line count
        line_count = float(self.chat_display.index(tk.END).split('.')[0])
        
        # If too many lines, remove some from the top
        if line_count > self.max_messages * 1.5:
            self.chat_display.configure(state=tk.NORMAL)
            # Remove first 100 lines
            self.chat_display.delete(1.0, "100.0")
            self.chat_display.configure(state=tk.DISABLED)
    
    def _add_example_messages(self):
        """Add example messages for testing"""
        example_messages = [
            ("StreamArtifact", "🌟 Stream Artifact is now online! Welcome to the cyberpunk future of AI chatbots!", "system"),
            ("Viewer123", "Hey everyone! First time here!", "chat", ["subscriber"]),
            ("ModeratorAI", "Welcome to the stream! Type !help for commands", "chat", ["moderator"]),
            ("TechUser", "This cyberpunk theme is amazing! How did you make it?", "chat"),
            ("StreamArtifact", "Thanks! It's built with Python and CustomTkinter with custom cyberpunk styling", "ai_response"),
            ("VIPUser", "!ai What's the weather like?", "command", ["vip"]),
            ("StreamArtifact", "I don't have access to real-time weather data, but I can help with other questions!", "ai_response"),
            ("CodeFan", "Check out this cool repo: https://github.com/Marek-Codex/Stream-Artifact", "chat"),
            ("StreamArtifact", "Type !ai followed by your question to interact with me!", "system")
        ]
        
        for i, (username, message, msg_type, *badges) in enumerate(example_messages):
            user_badges = badges[0] if badges else []
            # Add delay between messages for realistic feel
            self.chat_frame.after(i * 100, lambda u=username, m=message, t=msg_type, b=user_badges: self.add_message(u, m, message_type=t, user_badges=b))
    
    def update_user_count(self, count: int):
        """Update user count display"""
        # This would update a user count display
        pass
    
    def highlight_mention(self, username: str):
        """Highlight messages that mention a specific username"""
        # This would highlight messages containing @username
        pass
    
    def filter_messages(self, filter_type: str):
        """Filter messages by type"""
        # This would filter messages (show only AI responses, commands, etc.)
        pass
