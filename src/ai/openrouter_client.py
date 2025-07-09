"""
OpenRouter AI Client for Stream Artifact
Handles AI API communication and response generation
"""

import aiohttp
import asyncio
import json
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """OpenRouter API client for AI responses"""
    
    def __init__(self, api_key: str, model: str, database=None, config=None):
        self.api_key = api_key
        self.model = model
        self.database = database
        self.config = config
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Response caching and rate limiting
        self.last_request_time = datetime.now()
        self.request_count = 0
        self.rate_limit_window = timedelta(minutes=1)
        self.max_requests_per_window = 20
        
        # Context management
        self.context_cache: Dict[str, List[Dict]] = {}
        self.max_context_age = timedelta(hours=2)
        
        logger.info(f"🤖 OpenRouter client initialized with model: {model}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://stream-artifact.ai",
                "X-Title": "Stream Artifact Chatbot"
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def test_connection(self) -> bool:
        """Test the API connection"""
        try:
            session = await self._get_session()
            
            test_payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hello! This is a connection test."}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            async with session.post(f"{self.base_url}/chat/completions", json=test_payload) as response:
                if response.status == 200:
                    logger.info("✅ OpenRouter connection test successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ OpenRouter connection test failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ OpenRouter connection test error: {e}")
            return False
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models from OpenRouter"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    
                    for model in data.get("data", []):
                        models.append({
                            "id": model.get("id", ""),
                            "name": model.get("name", ""),
                            "description": model.get("description", ""),
                            "context_length": model.get("context_length", 4096),
                            "pricing": model.get("pricing", {})
                        })
                    
                    logger.info(f"📋 Retrieved {len(models)} available models")
                    return models
                else:
                    logger.error(f"❌ Failed to get models: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Error getting models: {e}")
            return []
    
    async def get_response(self, prompt: str, username: str, context: Dict = None) -> Optional[str]:
        """Get AI response for a prompt"""
        try:
            # Rate limiting check
            if not self._check_rate_limit():
                logger.warning("⚠️ Rate limit exceeded, skipping request")
                return None
            
            # Build context and messages
            messages = await self._build_messages(prompt, username, context or {})
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 150,  # Keep responses concise for chat
                "temperature": 0.8,
                "top_p": 0.9,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.3
            }
            
            # Make the API request
            session = await self._get_session()
            
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        ai_response = data["choices"][0]["message"]["content"].strip()
                        
                        # Clean and validate response
                        cleaned_response = self._clean_response(ai_response)
                        
                        # Store in memory
                        await self._store_memory(username, prompt, cleaned_response, context)
                        
                        logger.info(f"🤖 AI response generated for {username}")
                        return cleaned_response
                    else:
                        logger.warning("⚠️ No choices in AI response")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ AI API error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {e}")
            return None
    
    async def _build_messages(self, prompt: str, username: str, context: Dict) -> List[Dict]:
        """Build message history for AI context"""
        messages = []
        
        # System prompt with personality
        personality = "You are a friendly, helpful AI assistant for a Twitch stream. You engage naturally with viewers and provide helpful responses."
        if self.config and hasattr(self.config, 'ai') and hasattr(self.config.ai, 'personality'):
            personality = self.config.ai.personality
        
        system_prompt = f"""{personality}

Guidelines:
- Keep responses under 480 characters (Twitch limit)
- Be conversational and engaging
- Use the user's display name when appropriate
- Stay positive and supportive
- Avoid controversial topics
- If you don't know something, say so honestly"""
        
        # Add user context if available
        if context.get('display_name'):
            system_prompt += f"\n- The user's display name is: {context['display_name']}"
        
        if context.get('is_subscriber'):
            system_prompt += "\n- This user is a subscriber"
        
        if context.get('is_vip'):
            system_prompt += "\n- This user is a VIP"
        
        if context.get('is_mod'):
            system_prompt += "\n- This user is a moderator"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add recent conversation memory
        try:
            memory = await self.database.get_user_memory(username, limit=5)
            for mem in reversed(memory):  # Oldest first
                if mem['context']:
                    messages.append({"role": "user", "content": mem['context']})
                if mem['response']:
                    messages.append({"role": "assistant", "content": mem['response']})
        except Exception as e:
            logger.warning(f"⚠️ Could not load memory for {username}: {e}")
        
        # Add recent chat context for natural flow
        try:
            recent_messages = await self.database.get_recent_messages(
                context.get('channel', ''), limit=10
            )
            
            if recent_messages and not context.get('is_command'):
                context_text = "Recent chat context:\n"
                for msg in reversed(recent_messages[-5:]):  # Last 5 messages
                    if msg['username'] != username:  # Don't include the current user's messages
                        context_text += f"{msg['username']}: {msg['content']}\n"
                
                if len(context_text) > 50:  # Only add if there's meaningful context
                    messages.append({"role": "system", "content": context_text})
        except Exception as e:
            logger.warning(f"⚠️ Could not load chat context: {e}")
        
        # Add the current user prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate AI response"""
        # Remove common AI thinking patterns
        thinking_patterns = [
            r"\*thinks?\*.*?\*",
            r"\*.*?\*",
            r"\(thinking:.*?\)",
            r"\[thinking:.*?\]",
            r"Let me think about this\.\.\.",
            r"Hmm,?\s*let me see\.\.\.",
        ]
        
        for pattern in thinking_patterns:
            response = re.sub(pattern, "", response, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()
        
        # Ensure it's not too long for Twitch (480 char limit)
        if len(response) > 480:
            # Try to cut at a sentence boundary
            sentences = response.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + '. ') <= 470:  # Leave room for "..."
                    truncated += sentence + '. '
                else:
                    break
            
            if truncated:
                response = truncated.rstrip() + "..."
            else:
                response = response[:470] + "..."
        
        return response
    
    async def _store_memory(self, username: str, context: str, response: str, metadata: Dict):
        """Store conversation in memory"""
        try:
            # Calculate relevance score based on context
            relevance_score = 1.0
            
            # Higher relevance for commands
            if metadata.get('is_command'):
                relevance_score += 0.3
            
            # Higher relevance for VIPs/mods/subs
            if metadata.get('is_vip') or metadata.get('is_mod'):
                relevance_score += 0.2
            elif metadata.get('is_subscriber'):
                relevance_score += 0.1
            
            await self.database.add_ai_memory(
                username=username,
                context=context,
                response=response,
                relevance_score=relevance_score,
                memory_type='conversation',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Reset counter if window has passed
        if now - self.last_request_time > self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = now
        
        # Check if we can make another request
        if self.request_count >= self.max_requests_per_window:
            return False
        
        self.request_count += 1
        return True
    
    async def generate_personality(self, description: str) -> Optional[str]:
        """Generate a personality based on description"""
        try:
            prompt = f"""Analyze this personality description and create a concise, actionable personality for a Twitch chatbot. 

IMPORTANT INSTRUCTIONS:
1. Extract personality traits, speaking patterns, and behavioral characteristics
2. IGNORE and DO NOT MENTION any specific character names, movie titles, or game references
3. Focus on the underlying personality traits those references represent
4. Create a clean, actionable personality description under 200 words
5. Focus on communication style, tone, humor type, and interaction patterns

Input description:
{description}

Generate a clean personality description that captures the essence without referencing specific characters, movies, or games:"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert AI personality analyzer. You extract core personality traits while filtering out specific character, movie, and game references. Focus on underlying behavioral patterns, communication styles, and personality characteristics."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            session = await self._get_session()
            
            async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"].strip()
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating personality: {e}")
            return None
