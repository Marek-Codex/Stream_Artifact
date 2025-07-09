# Stream Artifact - Cyberpunk AI Chatbot

**A modern AI-powered Twitch chatbot with cyberpunk aesthetics and glassmorphism effects**

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 🌟 Features

### 🎮 Twitch Integration
- Real-time chat monitoring and response
- OAuth token authentication
- Command system with cooldowns
- User statistics and analytics
- Automatic reconnection

### 🤖 AI Capabilities
- OpenRouter API integration
- Multiple AI model support (GPT-4, Claude, Gemini)
- Conversation memory and context
- Personality customization
- Smart response timing

### 🎨 Cyberpunk UI
- Dark theme with neon accents
- Glassmorphism effects
- Glowing borders and animations
- Responsive design
- Real-time chat display

### ⚙️ Configuration
- Comprehensive settings GUI
- Multiple configuration tabs
- Real-time updates
- Persistent storage
- Easy setup wizard

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (tested)
- Twitch account with OAuth token
- OpenRouter API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YourUsername/stream-artifact.git
cd stream-artifact
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure settings:**
   - Copy `.env.example` to `.env`
   - Get your Twitch OAuth token from https://twitchapps.com/tmi/
   - Get your OpenRouter API key from https://openrouter.ai/
   - Update the `.env` file with your credentials

5. **Run the application:**
```bash
python main.py
```

## 📖 Configuration Guide

### Twitch Setup
1. Visit https://twitchapps.com/tmi/
2. Generate an OAuth token
3. Copy the token (including `oauth:` prefix)
4. Enter your channel name (without #)

### OpenRouter Setup
1. Sign up at https://openrouter.ai/
2. Create an API key
3. Choose your preferred AI model
4. Configure response parameters

### UI Customization
- **Theme**: Choose between cyberpunk, dark, or light
- **Effects**: Enable/disable glassmorphism and glow effects
- **Fonts**: Select from monospace font families
- **Colors**: Customize accent colors and themes

## 🎯 Usage

### Basic Commands
- `!ai <question>` - Ask the AI a question
- `!help` - Show available commands
- `!stats` - Display bot statistics
- `!uptime` - Show bot uptime

### AI Integration
The bot can respond to:
- Direct commands (`!ai`)
- @mentions
- Natural conversation (configurable)
- Context-aware responses

### Settings Panel
Access comprehensive settings through the GUI:
- **Twitch Tab**: Connection and chat settings
- **AI Tab**: Model selection and behavior
- **UI Tab**: Appearance and theme options
- **Commands Tab**: Enable/disable commands
- **Moderation Tab**: Auto-moderation settings

## 🏗️ Project Structure

```
stream-artifact/
├── src/
│   ├── core/
│   │   ├── app.py              # Main application class
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # SQLite database handler
│   │   └── twitch_client.py    # Twitch chat client
│   ├── ai/
│   │   └── openrouter_client.py # OpenRouter AI client
│   ├── ui/
│   │   ├── main_window.py      # Main GUI window
│   │   ├── chat_window.py      # Chat display widget
│   │   ├── settings_window.py  # Settings interface
│   │   └── components/
│   │       └── cyberpunk_widgets.py # Custom UI components
├── assets/                     # UI assets and icons
├── config/                     # Configuration files
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎨 Customization

### Themes
The application supports multiple themes:
- **Cyberpunk**: Dark with neon accents
- **Dark**: Standard dark theme
- **Light**: Light theme variant

### Color Scheme
Default cyberpunk colors:
- Primary: `#0a0a0a` (Deep black)
- Secondary: `#1a1a2e` (Dark blue-black)
- Accent: `#00d4ff` (Cyan)
- Success: `#00ff41` (Green)
- Error: `#ff4444` (Red)

### Custom Widgets
All UI components are custom-built with:
- Glassmorphism effects
- Hover animations
- Glow effects
- Responsive design

## 🔧 Development

### Architecture
- **Async/Await**: All I/O operations use asyncio
- **Threading**: GUI runs on main thread, async operations on background thread
- **Modular Design**: Separate modules for UI, AI, Twitch, and configuration
- **Type Hints**: Full type annotation support

### Key Classes
- `StreamArtifact`: Main application coordinator
- `TwitchClient`: Twitch chat integration
- `OpenRouterClient`: AI response generation
- `MainWindow`: Primary GUI interface
- `Config`: Configuration management

### Adding Features
1. Create new modules in appropriate directories
2. Follow the existing async/await patterns
3. Add configuration options to `config.py`
4. Update UI components as needed
5. Add tests for new functionality

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version (3.8+)
- Verify all dependencies are installed
- Check for syntax errors in configuration

**Twitch connection fails:**
- Verify OAuth token is correct
- Check channel name format (no #)
- Ensure stable internet connection

**AI responses not working:**
- Verify OpenRouter API key
- Check selected model availability
- Review rate limiting settings

**UI elements not displaying:**
- Check CustomTkinter installation
- Verify theme configuration
- Try resetting to defaults

### Debug Mode
Enable debug mode in settings or `.env`:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📊 Performance

### System Requirements
- **RAM**: 200MB+ (depends on AI model)
- **CPU**: Modern multi-core processor
- **Storage**: 100MB+ for application and logs
- **Network**: Stable internet for Twitch/AI APIs

### Optimization
- Async operations prevent UI blocking
- Message caching reduces API calls
- Efficient database queries
- Minimal resource usage

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Include error handling

### Testing
- Run existing tests
- Add tests for new features
- Test on multiple Python versions
- Verify UI responsiveness

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CustomTkinter**: Modern UI framework
- **TwitchIO**: Twitch chat integration
- **OpenRouter**: AI model access
- **Rich**: Beautiful logging
- **Aiohttp**: Async HTTP client

## 🔗 Links

- [Documentation](https://github.com/YourUsername/stream-artifact/wiki)
- [Issues](https://github.com/YourUsername/stream-artifact/issues)
- [Discussions](https://github.com/YourUsername/stream-artifact/discussions)
- [Releases](https://github.com/YourUsername/stream-artifact/releases)

## 📧 Support

For support, please:
1. Check the [Wiki](https://github.com/YourUsername/stream-artifact/wiki)
2. Search existing [Issues](https://github.com/YourUsername/stream-artifact/issues)
3. Create a new issue with details
4. Join our [Discord](https://discord.gg/your-server) community

---

**Made with ❤️ for the streaming community**

*Stream Artifact - Where cyberpunk meets AI-powered chat*
