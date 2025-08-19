# Claude Code Documentation Mirror

> **Originally created by [Eric Buess](https://github.com/ericbuess)** - [Original Repository](https://github.com/ericbuess/claude-code-docs)
>
> This is a Windows-focused fork that maintains the same functionality with enhanced Windows support.


[![Last Update](https://img.shields.io/github/last-commit/ericbuess/claude-code-docs/main.svg?label=docs%20updated)](https://github.com/ericbuess/claude-code-docs/commits/main)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)]()
[![Beta](https://img.shields.io/badge/status-early%20beta-orange)](https://github.com/ericbuess/claude-code-docs/issues)

Local mirror of Claude Code documentation files from https://docs.anthropic.com/en/docs/claude-code/, updated every 3 hours.

## ⚠️ Early Beta Notice

**This is an early beta release**. There may be errors or unexpected behavior. If you encounter any issues, please [open an issue](https://github.com/ericbuess/claude-code-docs/issues) - your feedback helps improve the tool!

## 🆕 Version 0.4.0 - Windows Support!

**New in this version:**
- 🪟 **Windows Support**: Full Windows compatibility using Python-based installer
- 🐍 **Cross-platform Python**: Unified codebase works on Windows, macOS, and Linux
- 📋 **Claude Code Changelog**: Access the official Claude Code release notes with `/docs changelog`
- 🔧 **Improved installer**: Better handling of updates and edge cases

To update, use the appropriate command for your platform (see Installation section below).

## Why This Exists

- **Faster access** - Reads from local files instead of fetching from web
- **Automatic updates** - Attempts to stay current with the latest documentation
- **Track changes** - See what changed in docs over time
- **Claude Code changelog** - Quick access to official release notes and version history
- **Better Claude Code integration** - Allows Claude to explore documentation more effectively

## Platform Compatibility

- ✅ **Windows**: Fully supported with Python installer (Windows 10/11)
- ✅ **macOS**: Fully supported (tested on macOS 12+)
- ✅ **Linux**: Fully supported (Ubuntu, Debian, Fedora, etc.)

### Prerequisites

**All platforms:**
- **Python 3.7+** - Required for cross-platform compatibility
- **Git** - For cloning and updating the repository
- **Claude Code** - Obviously :)

**Platform-specific notes:**
- **Windows**: Python must be in your PATH (check "Add Python to PATH" during installation)
- **macOS/Linux**: Python and Git are usually pre-installed
- **Optional**: `requests` library (`pip install requests`) for enhanced features

## Installation

### Windows

**Option 1: Download and run installer**
```powershell
# Download the installer
curl -o install.py https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py
# Run it
python install.py
```

**Option 2: Clone and install**
```powershell
git clone https://github.com/ericbuess/claude-code-docs.git
cd claude-code-docs
python install.py
# Or double-click install.bat
```

### macOS/Linux

**Option 1: Shell installer (traditional)**
```bash
curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.sh | bash
```

**Option 2: Python installer (new, cross-platform)**
```bash
curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py | python3
```

The installer will:
1. Install to `~/.claude-code-docs` (or `%USERPROFILE%\.claude-code-docs` on Windows)
2. Create the `/docs` slash command
3. Set up auto-update hooks for keeping docs current

**Note**: The command is `/docs (user)` - it will show in your command list with "(user)" after it to indicate it's a user-created command.

## Usage

The `/docs` command provides instant access to documentation with optional freshness checking.

### Default: Lightning-fast access (no checks)
```bash
/docs hooks        # Instantly read hooks documentation
/docs mcp          # Instantly read MCP documentation
/docs memory       # Instantly read memory documentation
```

You'll see: `📚 Reading from local docs (run /docs -t to check freshness)`

### Check documentation sync status with -t flag
```bash
/docs -t           # Show sync status with GitHub
/docs -t hooks     # Check sync status, then read hooks docs
/docs -t mcp       # Check sync status, then read MCP docs
```

### See what's new
```bash
/docs what's new   # Show recent documentation changes with diffs
```

### Read Claude Code changelog
```bash
/docs changelog    # Read official Claude Code release notes and version history
```

The changelog feature fetches the latest release notes directly from the official Claude Code repository, showing you what's new in each version.

### Uninstall
```bash
/docs uninstall    # Get commnd to remove claude-code-docs completely
```

### Creative usage examples
```bash
# Natural language queries work great
/docs what environment variables exist and how do I use them?
/docs explain the differences between hooks and MCP

# Check for recent changes
/docs -t what's new in the latest documentation?
/docs changelog    # Check Claude Code release notes

# Search across all docs
/docs find all mentions of authentication
/docs how do I customize Claude Code's behavior?
```

## How Updates Work

The documentation attempts to stay current:
- GitHub Actions runs periodically to fetch new documentation
- When you use `/docs`, it checks for updates
- Updates are pulled when available
- You may see "🔄 Updating documentation..." when this happens

Note: If automatic updates fail, you can always run the installer again to get the latest version.

## Updating from Previous Versions

### Windows
```powershell
curl -o install.py https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py
python install.py
```

### macOS/Linux
```bash
# Using shell installer
curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.sh | bash
# Or using Python installer
curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py | python3
```

The installer will automatically detect and migrate existing installations.

## Troubleshooting

### Command not found
If `/docs` returns "command not found":
1. Check if the command file exists: `ls ~/.claude/commands/docs.md`
2. Restart Claude Code to reload commands
3. Re-run the installation script

### Documentation not updating
If documentation seems outdated:
1. Run `/docs -t` to check sync status and force an update
2. Manually update: `cd ~/.claude-code-docs && git pull`
3. Check if GitHub Actions are running: [View Actions](https://github.com/ericbuess/claude-code-docs/actions)

### Installation errors
- **"Python is not installed"**: Install Python 3.7+ from https://www.python.org/downloads/
- **"Git not found"**: Install Git from https://git-scm.com/downloads
- **"Failed to clone repository"**: Check your internet connection
- **"Failed to update settings.json"**: Check file permissions on `~/.claude/settings.json` (or `%USERPROFILE%\.claude\settings.json` on Windows)
- **Windows: "python not recognized"**: Ensure Python is added to PATH during installation

## Uninstalling

To completely remove the docs integration:

```bash
/docs uninstall
```

Or run directly:

**Windows:**
```powershell
python %USERPROFILE%\.claude-code-docs\uninstall.py
# Or double-click uninstall.bat in the installation directory
```

**macOS/Linux:**
```bash
python ~/.claude-code-docs/uninstall.py
# Or use the shell script if it exists:
~/.claude-code-docs/uninstall.sh
```

See [UNINSTALL.md](UNINSTALL.md) for manual uninstall instructions.

## Security Notes

- The installer modifies `~/.claude/settings.json` to add an auto-update hook
- The hook only runs `git pull` when reading documentation files
- All operations are limited to the documentation directory
- No data is sent externally - everything is local
- **Repository Trust**: The installer clones from GitHub over HTTPS. For additional security, you can:
  - Fork the repository and install from your own fork
  - Clone manually and run the installer from the local directory
  - Review all code before installation

## What's New

### v0.4.0 (Latest)
- 🪟 **Windows Support**: Full Windows compatibility with Python-based implementation
- 🐍 **Cross-platform**: Unified Python codebase for all platforms
- 🔧 **New installers**: Python-based install.py, uninstall.py, and helper scripts
- 📦 **Batch wrappers**: Windows .bat files for easy double-click installation
- 🔄 **Backward compatible**: Existing macOS/Linux installations continue to work

### v0.3.3
- Added Claude Code changelog integration (`/docs changelog`)
- Fixed shell compatibility for macOS users (zsh/bash)
- Improved documentation and error messages
- Added platform compatibility badges

### v0.3.2
- Fixed automatic update functionality  
- Improved handling of local repository changes
- Better error recovery during updates

## Contributing

**Contributions are welcome!** This is a community project and we'd love your help:

- ✅ **Windows Support**: Now available! Help us test and improve it
- 🐛 **Bug Reports**: Found something not working? [Open an issue](https://github.com/ericbuess/claude-code-docs/issues)
- 💡 **Feature Requests**: Have an idea? [Start a discussion](https://github.com/ericbuess/claude-code-docs/issues)
- 📝 **Documentation**: Help improve docs or add examples

You can also use Claude Code itself to help build features - just fork the repo and let Claude assist you!

## Known Issues

As this is an early beta, you might encounter some issues:
- Auto-updates may occasionally fail on some network configurations
- Some documentation links might not resolve correctly

If you find any issues not listed here, please [report them](https://github.com/ericbuess/claude-code-docs/issues)!

## License

Documentation content belongs to Anthropic.
This mirror tool is open source - contributions welcome!
