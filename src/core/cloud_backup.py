"""
Cloud Backup Service for Stream Artifact
Handles backing up bot configuration to cloud services
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class CloudBackupService:
    """Cloud backup service for bot configurations"""
    
    def __init__(self, config):
        self.config = config
        self.github_token = None
        self.backup_gist_id = None
        
        logger.info("☁️ Cloud backup service initialized")
    
    def set_github_credentials(self, access_token: str):
        """Set GitHub credentials for backup"""
        self.github_token = access_token
        logger.info("🔑 GitHub credentials configured")
    
    async def backup_configuration(self, config_data: Dict) -> bool:
        """Backup configuration to cloud"""
        try:
            if not self.github_token:
                logger.warning("⚠️ No GitHub token configured")
                return False
            
            # Prepare backup data
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'application': 'Stream Artifact',
                'config': config_data
            }
            
            # Create or update GitHub Gist
            success = await self._backup_to_github_gist(backup_data)
            
            if success:
                logger.info("✅ Configuration backed up to cloud")
                return True
            else:
                logger.error("❌ Failed to backup configuration")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backup error: {e}")
            return False
    
    async def restore_configuration(self) -> Optional[Dict]:
        """Restore configuration from cloud"""
        try:
            if not self.github_token:
                logger.warning("⚠️ No GitHub token configured")
                return None
            
            # Get backup from GitHub Gist
            backup_data = await self._restore_from_github_gist()
            
            if backup_data and 'config' in backup_data:
                logger.info("✅ Configuration restored from cloud")
                return backup_data['config']
            else:
                logger.warning("⚠️ No backup found or backup is invalid")
                return None
                
        except Exception as e:
            logger.error(f"❌ Restore error: {e}")
            return None
    
    async def _backup_to_github_gist(self, backup_data: Dict) -> bool:
        """Backup to GitHub Gist"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                }
                
                # Prepare gist data
                gist_data = {
                    'description': 'Stream Artifact Bot Configuration Backup',
                    'public': False,  # Private gist
                    'files': {
                        'stream-artifact-config.json': {
                            'content': json.dumps(backup_data, indent=2)
                        }
                    }
                }
                
                # Create or update gist
                if self.backup_gist_id:
                    # Update existing gist
                    url = f'https://api.github.com/gists/{self.backup_gist_id}'
                    method = session.patch
                else:
                    # Create new gist
                    url = 'https://api.github.com/gists'
                    method = session.post
                
                async with method(url, json=gist_data, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        result = await resp.json()
                        self.backup_gist_id = result['id']
                        
                        # Save gist ID to config
                        self.config.set('cloud.backup_gist_id', self.backup_gist_id)
                        self.config.save()
                        
                        logger.info(f"✅ Backup saved to gist: {self.backup_gist_id}")
                        return True
                    else:
                        error_text = await resp.text()
                        logger.error(f"❌ GitHub API error: {resp.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ GitHub backup error: {e}")
            return False
    
    async def _restore_from_github_gist(self) -> Optional[Dict]:
        """Restore from GitHub Gist"""
        try:
            # Get gist ID from config
            gist_id = self.config.get('cloud.backup_gist_id')
            if not gist_id:
                logger.warning("⚠️ No backup gist ID found")
                return None
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = f'https://api.github.com/gists/{gist_id}'
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        
                        # Extract configuration from gist
                        files = result.get('files', {})
                        config_file = files.get('stream-artifact-config.json')
                        
                        if config_file and 'content' in config_file:
                            backup_data = json.loads(config_file['content'])
                            logger.info("✅ Configuration restored from gist")
                            return backup_data
                        else:
                            logger.error("❌ No configuration found in gist")
                            return None
                    else:
                        error_text = await resp.text()
                        logger.error(f"❌ GitHub API error: {resp.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ GitHub restore error: {e}")
            return None
    
    async def list_backups(self) -> list:
        """List available backups"""
        try:
            if not self.github_token:
                return []
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                # Get all gists
                url = 'https://api.github.com/gists'
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        gists = await resp.json()
                        
                        # Filter Stream Artifact backups
                        backups = []
                        for gist in gists:
                            if 'stream-artifact-config.json' in gist.get('files', {}):
                                backups.append({
                                    'id': gist['id'],
                                    'description': gist['description'],
                                    'created_at': gist['created_at'],
                                    'updated_at': gist['updated_at']
                                })
                        
                        return backups
                    else:
                        logger.error(f"❌ Failed to list gists: {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"❌ List backups error: {e}")
            return []
    
    async def delete_backup(self, gist_id: str) -> bool:
        """Delete a backup"""
        try:
            if not self.github_token:
                return False
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'token {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                url = f'https://api.github.com/gists/{gist_id}'
                
                async with session.delete(url, headers=headers) as resp:
                    if resp.status == 204:
                        logger.info(f"✅ Backup deleted: {gist_id}")
                        return True
                    else:
                        logger.error(f"❌ Failed to delete backup: {resp.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Delete backup error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if cloud backup is configured"""
        return bool(self.github_token)
    
    def get_backup_info(self) -> Dict:
        """Get backup service information"""
        return {
            'service': 'GitHub Gists',
            'configured': self.is_configured(),
            'gist_id': self.backup_gist_id,
            'last_backup': self.config.get('cloud.last_backup_time')
        }


class LocalBackupService:
    """Local backup service for bot configurations"""
    
    def __init__(self, config):
        self.config = config
        self.backup_dir = config.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info("💾 Local backup service initialized")
    
    async def backup_configuration(self, config_data: Dict) -> bool:
        """Backup configuration locally"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.json"
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'application': 'Stream Artifact',
                'config': config_data
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            # Keep only last 10 backups
            await self._cleanup_old_backups()
            
            logger.info(f"✅ Configuration backed up locally: {backup_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Local backup error: {e}")
            return False
    
    async def restore_configuration(self, backup_file: str = None) -> Optional[Dict]:
        """Restore configuration from local backup"""
        try:
            if backup_file:
                backup_path = self.backup_dir / backup_file
            else:
                # Get latest backup
                backup_files = list(self.backup_dir.glob("backup_*.json"))
                if not backup_files:
                    logger.warning("⚠️ No local backups found")
                    return None
                
                backup_path = max(backup_files, key=lambda x: x.stat().st_mtime)
            
            if backup_path.exists():
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                if 'config' in backup_data:
                    logger.info(f"✅ Configuration restored from: {backup_path.name}")
                    return backup_data['config']
                else:
                    logger.error("❌ Invalid backup file format")
                    return None
            else:
                logger.warning(f"⚠️ Backup file not found: {backup_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Local restore error: {e}")
            return None
    
    async def list_backups(self) -> list:
        """List available local backups"""
        try:
            backup_files = list(self.backup_dir.glob("backup_*.json"))
            backups = []
            
            for backup_file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    backups.append({
                        'file': backup_file.name,
                        'timestamp': backup_data.get('timestamp'),
                        'size': backup_file.stat().st_size,
                        'created': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read backup {backup_file}: {e}")
            
            return backups
            
        except Exception as e:
            logger.error(f"❌ List local backups error: {e}")
            return []
    
    async def delete_backup(self, backup_file: str) -> bool:
        """Delete a local backup"""
        try:
            backup_path = self.backup_dir / backup_file
            if backup_path.exists():
                backup_path.unlink()
                logger.info(f"✅ Local backup deleted: {backup_file}")
                return True
            else:
                logger.warning(f"⚠️ Backup file not found: {backup_file}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delete local backup error: {e}")
            return False
    
    async def _cleanup_old_backups(self, keep_count: int = 10):
        """Keep only the most recent backups"""
        try:
            backup_files = sorted(
                self.backup_dir.glob("backup_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Delete old backups
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                logger.info(f"🗑️ Deleted old backup: {old_backup.name}")
                
        except Exception as e:
            logger.error(f"❌ Cleanup old backups error: {e}")
    
    def is_configured(self) -> bool:
        """Check if local backup is configured"""
        return self.backup_dir.exists()
    
    def get_backup_info(self) -> Dict:
        """Get backup service information"""
        backup_count = len(list(self.backup_dir.glob("backup_*.json")))
        return {
            'service': 'Local Storage',
            'configured': self.is_configured(),
            'backup_directory': str(self.backup_dir),
            'backup_count': backup_count
        }
