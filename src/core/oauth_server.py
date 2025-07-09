"""
OAuth Server for Stream Artifact
Simple HTTP server to handle OAuth callbacks
"""

import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from typing import Optional, Dict, Callable
import urllib.parse
import secrets
import hashlib
import base64

logger = logging.getLogger(__name__)


class OAuthServer:
    """Simple OAuth callback server"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.callback_handlers = {}
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"🔐 OAuth server initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/auth/twitch', self._handle_twitch_callback)
        self.app.router.add_get('/auth/github', self._handle_github_callback)
        self.app.router.add_get('/auth/openrouter', self._handle_openrouter_callback)
        self.app.router.add_get('/success', self._handle_success)
        self.app.router.add_get('/error', self._handle_error)
        
        # Serve static files for OAuth pages
        self.app.router.add_static('/', path='assets/oauth', name='oauth')
    
    async def start(self):
        """Start the OAuth server"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"🚀 OAuth server started on http://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start OAuth server: {e}")
            raise
    
    async def stop(self):
        """Stop the OAuth server"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            
            logger.info("🛑 OAuth server stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping OAuth server: {e}")
    
    def register_callback(self, service: str, callback: Callable):
        """Register a callback for OAuth completion"""
        self.callback_handlers[service] = callback
        logger.info(f"📝 Registered callback for {service}")
    
    async def _handle_twitch_callback(self, request):
        """Handle Twitch OAuth callback"""
        try:
            # Extract parameters
            code = request.query.get('code')
            state = request.query.get('state')
            error = request.query.get('error')
            
            if error:
                logger.error(f"❌ Twitch OAuth error: {error}")
                return web.Response(text=self._error_page(error), content_type='text/html')
            
            if not code:
                logger.error("❌ No authorization code received")
                return web.Response(text=self._error_page("No authorization code"), content_type='text/html')
            
            # Exchange code for token
            token_data = await self._exchange_twitch_code(code)
            
            if token_data:
                # Get user info
                user_info = await self._get_twitch_user_info(token_data['access_token'])
                
                # Combine data
                oauth_result = {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'user_info': user_info,
                    'scope': token_data.get('scope', [])
                }
                
                # Call registered callback
                if 'twitch' in self.callback_handlers:
                    await self.callback_handlers['twitch'](oauth_result)
                
                logger.info("✅ Twitch OAuth successful")
                return web.Response(text=self._success_page("Twitch"), content_type='text/html')
            else:
                logger.error("❌ Failed to exchange Twitch code for token")
                return web.Response(text=self._error_page("Token exchange failed"), content_type='text/html')
            
        except Exception as e:
            logger.error(f"❌ Twitch callback error: {e}")
            return web.Response(text=self._error_page(str(e)), content_type='text/html')
    
    async def _handle_github_callback(self, request):
        """Handle GitHub OAuth callback"""
        try:
            code = request.query.get('code')
            state = request.query.get('state')
            error = request.query.get('error')
            
            if error:
                logger.error(f"❌ GitHub OAuth error: {error}")
                return web.Response(text=self._error_page(error), content_type='text/html')
            
            if not code:
                logger.error("❌ No authorization code received")
                return web.Response(text=self._error_page("No authorization code"), content_type='text/html')
            
            # Exchange code for token
            token_data = await self._exchange_github_code(code)
            
            if token_data:
                # Get user info
                user_info = await self._get_github_user_info(token_data['access_token'])
                
                oauth_result = {
                    'access_token': token_data['access_token'],
                    'user_info': user_info,
                    'scope': token_data.get('scope', [])
                }
                
                # Call registered callback
                if 'github' in self.callback_handlers:
                    await self.callback_handlers['github'](oauth_result)
                
                logger.info("✅ GitHub OAuth successful")
                return web.Response(text=self._success_page("GitHub"), content_type='text/html')
            else:
                logger.error("❌ Failed to exchange GitHub code for token")
                return web.Response(text=self._error_page("Token exchange failed"), content_type='text/html')
            
        except Exception as e:
            logger.error(f"❌ GitHub callback error: {e}")
            return web.Response(text=self._error_page(str(e)), content_type='text/html')
    
    async def _handle_openrouter_callback(self, request):
        """Handle OpenRouter OAuth callback (if they implement OAuth)"""
        try:
            # For now, OpenRouter uses API keys, but this is ready for future OAuth support
            api_key = request.query.get('api_key')
            
            if api_key:
                # Test the API key
                if await self._test_openrouter_key(api_key):
                    oauth_result = {
                        'api_key': api_key,
                        'service': 'openrouter'
                    }
                    
                    # Call registered callback
                    if 'openrouter' in self.callback_handlers:
                        await self.callback_handlers['openrouter'](oauth_result)
                    
                    logger.info("✅ OpenRouter API key validated")
                    return web.Response(text=self._success_page("OpenRouter"), content_type='text/html')
                else:
                    logger.error("❌ Invalid OpenRouter API key")
                    return web.Response(text=self._error_page("Invalid API key"), content_type='text/html')
            else:
                logger.error("❌ No API key provided")
                return web.Response(text=self._error_page("No API key"), content_type='text/html')
            
        except Exception as e:
            logger.error(f"❌ OpenRouter callback error: {e}")
            return web.Response(text=self._error_page(str(e)), content_type='text/html')
    
    async def _exchange_twitch_code(self, code: str) -> Optional[Dict]:
        """Exchange Twitch authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'client_id': 'your_twitch_client_id',  # Replace with your client ID
                    'client_secret': 'your_twitch_client_secret',  # Replace with your client secret
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': f'http://{self.host}:{self.port}/auth/twitch'
                }
                
                async with session.post('https://id.twitch.tv/oauth2/token', data=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"❌ Twitch token exchange failed: {resp.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Twitch token exchange error: {e}")
            return None
    
    async def _get_twitch_user_info(self, access_token: str) -> Optional[Dict]:
        """Get Twitch user information"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Client-Id': 'your_twitch_client_id'
                }
                
                async with session.get('https://api.twitch.tv/helix/users', headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['data'][0] if data['data'] else None
                    else:
                        logger.error(f"❌ Twitch user info failed: {resp.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Twitch user info error: {e}")
            return None
    
    async def _exchange_github_code(self, code: str) -> Optional[Dict]:
        """Exchange GitHub authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    'client_id': 'your_github_client_id',  # Replace with your client ID
                    'client_secret': 'your_github_client_secret',  # Replace with your client secret
                    'code': code
                }
                
                headers = {'Accept': 'application/json'}
                
                async with session.post('https://github.com/login/oauth/access_token', data=data, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"❌ GitHub token exchange failed: {resp.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ GitHub token exchange error: {e}")
            return None
    
    async def _get_github_user_info(self, access_token: str) -> Optional[Dict]:
        """Get GitHub user information"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {access_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                async with session.get('https://api.github.com/user', headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.error(f"❌ GitHub user info failed: {resp.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ GitHub user info error: {e}")
            return None
    
    async def _test_openrouter_key(self, api_key: str) -> bool:
        """Test OpenRouter API key"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Test with a simple request
                data = {
                    'model': 'gpt-3.5-turbo',
                    'messages': [{'role': 'user', 'content': 'test'}],
                    'max_tokens': 5
                }
                
                async with session.post('https://openrouter.ai/api/v1/chat/completions', json=data, headers=headers) as resp:
                    return resp.status == 200
                    
        except Exception as e:
            logger.error(f"❌ OpenRouter API key test error: {e}")
            return False
    
    async def _handle_success(self, request):
        """Handle success page"""
        return web.Response(text=self._success_page("Authorization"), content_type='text/html')
    
    async def _handle_error(self, request):
        """Handle error page"""
        error = request.query.get('error', 'Unknown error')
        return web.Response(text=self._error_page(error), content_type='text/html')
    
    def _success_page(self, service: str) -> str:
        """Generate success page HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Stream Artifact - Success</title>
            <style>
                body {{
                    font-family: 'Consolas', monospace;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                    color: #ffffff;
                    margin: 0;
                    padding: 40px;
                    text-align: center;
                }}
                .container {{
                    max-width: 500px;
                    margin: 0 auto;
                    background: rgba(26, 26, 46, 0.8);
                    padding: 40px;
                    border-radius: 10px;
                    border: 2px solid #00d4ff;
                    box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                }}
                .success-icon {{
                    font-size: 64px;
                    color: #00ff41;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 24px;
                    color: #00ff41;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #b0b0b0;
                    margin-bottom: 30px;
                }}
                .close-btn {{
                    background: #00d4ff;
                    color: #0a0a0a;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .close-btn:hover {{
                    background: #ffffff;
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <div class="title">SUCCESS!</div>
                <div class="message">
                    {service} has been connected successfully!<br>
                    You can now close this window and return to Stream Artifact.
                </div>
                <button class="close-btn" onclick="window.close()">Close Window</button>
            </div>
            <script>
                setTimeout(() => {{
                    window.close();
                }}, 3000);
            </script>
        </body>
        </html>
        """
    
    def _error_page(self, error: str) -> str:
        """Generate error page HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Stream Artifact - Error</title>
            <style>
                body {{
                    font-family: 'Consolas', monospace;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                    color: #ffffff;
                    margin: 0;
                    padding: 40px;
                    text-align: center;
                }}
                .container {{
                    max-width: 500px;
                    margin: 0 auto;
                    background: rgba(26, 26, 46, 0.8);
                    padding: 40px;
                    border-radius: 10px;
                    border: 2px solid #ff4444;
                    box-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
                }}
                .error-icon {{
                    font-size: 64px;
                    color: #ff4444;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 24px;
                    color: #ff4444;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #b0b0b0;
                    margin-bottom: 30px;
                }}
                .error-details {{
                    background: rgba(255, 68, 68, 0.1);
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    font-size: 14px;
                    color: #ff4444;
                }}
                .close-btn {{
                    background: #ff4444;
                    color: #ffffff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .close-btn:hover {{
                    background: #ff6666;
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <div class="title">AUTHENTICATION ERROR</div>
                <div class="message">
                    There was an error connecting your account.
                </div>
                <div class="error-details">
                    Error: {error}
                </div>
                <button class="close-btn" onclick="window.close()">Close Window</button>
            </div>
            <script>
                setTimeout(() => {{
                    window.close();
                }}, 5000);
            </script>
        </body>
        </html>
        """
