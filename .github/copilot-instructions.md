# Copilot Instructions for Stream Artifact - Cyberpunk AI Chatbot

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a standalone Python desktop application for a modern AI-powered Twitch chatbot using OpenRouter API. The application features a cyberpunk/hackercore aesthetic with glassmorphism effects.

## Architecture Guidelines
- **UI Framework**: Use CustomTkinter for modern, themed UI components with cyberpunk styling
- **Async Programming**: Use asyncio for all I/O operations (Twitch chat, API calls)
- **AI Integration**: OpenRouter API for multiple AI model support
- **Database**: SQLite for local storage of settings, memory, and user data
- **Twitch Integration**: twitchio library for chat connection and management

## Design System
- **Theme**: Dark cyberpunk with glassmorphism effects
- **Colors**: Deep blues, purples, neon accents (cyan, magenta, green)
- **Effects**: Subtle glows, shadows, transparency, rounded corners
- **Typography**: Monospace fonts for code/terminal feel
- **Layout**: Modern card-based layout with proper spacing

## Code Style
- Use type hints for all functions and methods
- Follow async/await patterns for I/O operations
- Use dataclasses for configuration and data structures
- Implement proper error handling and logging
- Use context managers for resource management

## Key Features to Implement
1. Real-time Twitch chat integration
2. OpenRouter AI responses with memory/context
3. Command system with permissions
4. User management and analytics
5. Beautiful cyberpunk GUI with glassmorphism
6. Settings management and persistence
7. Moderation tools and filters
8. Performance monitoring and logging

## Dependencies
- customtkinter: Modern UI framework
- twitchio: Twitch chat integration
- aiohttp: Async HTTP client for OpenRouter
- sqlite3: Database operations
- asyncio: Async programming
- tkinter: Base GUI framework
- Pillow: Image processing for UI effects
