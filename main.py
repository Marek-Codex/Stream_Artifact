#!/usr/bin/env python3
"""
Stream Artifact - Cyberpunk AI Chatbot
A modern AI-powered Twitch chatbot with cyberpunk aesthetics

Created by MarekCodex
https://github.com/Marek-Codex
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.app import StreamArtifact

def main():
    """Main entry point for Stream Artifact"""
    try:
        # Create and run the application
        app = StreamArtifact()
        app.run()
    except KeyboardInterrupt:
        print("\n🌟 Stream Artifact shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
