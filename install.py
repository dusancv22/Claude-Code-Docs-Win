#!/usr/bin/env python3
"""
Claude Code Docs Installer - Cross-platform Python implementation
Supports Windows, macOS, and Linux
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Fix Windows console encoding for Unicode
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Version and configuration
VERSION = "0.4.0"
REPO_URL = "https://github.com/ericbuess/claude-code-docs.git"
INSTALL_BRANCH = "main"

# Cross-platform paths
HOME = Path.home()
INSTALL_DIR = HOME / ".claude-code-docs"
CLAUDE_DIR = HOME / ".claude"
COMMANDS_DIR = CLAUDE_DIR / "commands"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
COMMAND_FILE = COMMANDS_DIR / "docs.md"


def print_header():
    """Print installation header"""
    print(f"Claude Code Docs Installer v{VERSION}")
    print("=" * 40)
    print(f"[OK] Detected {platform.system()}")
    print()


def check_dependencies() -> bool:
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print(f"[ERROR] Error: Python 3.7+ required (found {sys.version})")
        return False
    
    # Check for git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("[OK] Git found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Error: Git is required but not installed")
        print("  Please install Git from: https://git-scm.com/downloads")
        return False
    
    # Check for requests library (optional but recommended)
    try:
        import requests
        print("[OK] Python requests library found")
    except ImportError:
        print("[WARNING]  Warning: 'requests' library not found")
        print("  Install with: pip install requests")
        print("  Continuing without it (may affect some features)...")
    
    print("[OK] All required dependencies satisfied")
    return True


def find_existing_installations() -> List[Path]:
    """Find any existing claude-code-docs installations"""
    installations = []
    
    # Check command file for paths
    if COMMAND_FILE.exists():
        try:
            content = COMMAND_FILE.read_text()
            # Look for various installation path patterns
            import re
            patterns = [
                r'Execute.*?([/\\].*?claude-code-docs)',
                r'LOCAL DOCS AT:\s*([^\s]+)/docs/',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    path = Path(match.replace('~', str(HOME)))
                    if path.exists() and path.is_dir():
                        installations.append(path)
        except Exception:
            pass
    
    # Check settings.json hooks for paths
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            
            hooks = settings.get('hooks', {}).get('PreToolUse', [])
            for hook_entry in hooks:
                for hook in hook_entry.get('hooks', []):
                    command = hook.get('command', '')
                    if 'claude-code-docs' in command:
                        # Extract path from command
                        import re
                        match = re.search(r'([/\\].*?claude-code-docs)', command)
                        if match:
                            path = Path(match.group(1).replace('~', str(HOME)))
                            if path.exists() and path.is_dir():
                                installations.append(path)
        except Exception:
            pass
    
    # Check current directory if running from an installation
    current_dir = Path.cwd()
    if (current_dir / "docs" / "docs_manifest.json").exists() and current_dir != INSTALL_DIR:
        installations.append(current_dir)
    
    # Deduplicate and exclude new location
    unique_installations = []
    for path in installations:
        if path != INSTALL_DIR and path not in unique_installations:
            unique_installations.append(path)
    
    return unique_installations


def git_operation(args: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
    """Execute git operation in a cross-platform way"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def migrate_installation(old_dir: Path):
    """Migrate from old installation to new location"""
    print(f"[INFO] Found existing installation at: {old_dir}")
    print(f"   Migrating to: {INSTALL_DIR}")
    print()
    
    # Check for uncommitted changes
    should_preserve = False
    if (old_dir / ".git").exists():
        success, output = git_operation(["status", "--porcelain"], cwd=old_dir)
        if success and output:
            should_preserve = True
            print("[WARNING]  Uncommitted changes detected in old installation")
    
    # Fresh install at new location
    print("Installing fresh at ~/.claude-code-docs...")
    success, output = git_operation(["clone", "-b", INSTALL_BRANCH, REPO_URL, str(INSTALL_DIR)])
    if not success:
        print(f"[ERROR] Failed to clone repository: {output}")
        sys.exit(1)
    
    # Remove old directory if safe
    if not should_preserve:
        try:
            shutil.rmtree(old_dir)
            print("[OK] Old installation removed")
        except Exception as e:
            print(f"[WARNING]  Could not remove old installation: {e}")
    else:
        print(f"[INFO] Old installation preserved at: {old_dir}")
        print("   (has uncommitted changes)")
    
    print()
    print("[SUCCESS] Migration complete!")


def safe_git_update() -> bool:
    """Safely update the git repository"""
    os.chdir(INSTALL_DIR)
    
    # Get current branch
    success, current_branch = git_operation(["rev-parse", "--abbrev-ref", "HEAD"])
    if not success:
        current_branch = "unknown"
    
    target_branch = INSTALL_BRANCH
    
    if current_branch != target_branch:
        print(f"  Switching from {current_branch} to {target_branch} branch...")
    else:
        print(f"  Updating {target_branch} branch...")
    
    # Try regular pull first
    print("Updating to latest version...")
    success, output = git_operation(["pull", "--quiet", "origin", target_branch])
    
    if success:
        return True
    
    # If pull failed, try more aggressive approach
    print("  Standard update failed, trying harder...")
    
    # Fetch latest
    success, output = git_operation(["fetch", "origin", target_branch])
    if not success:
        print("  [WARNING]  Could not fetch from GitHub (offline?)")
        return False
    
    # Check for local changes
    success, status = git_operation(["status", "--porcelain"])
    has_changes = bool(status) if success else False
    
    if has_changes:
        # Check if it's just manifest changes (expected)
        non_manifest_changes = [line for line in status.splitlines() 
                               if "docs_manifest.json" not in line and "docs\\docs_manifest.json" not in line]
        
        if non_manifest_changes:
            print()
            print("[WARNING]  WARNING: Local changes detected in your installation:")
            print()
            print("The installer will reset to a clean state, discarding these changes.")
            print()
            response = input("Continue and discard local changes? [y/N]: ")
            if response.lower() != 'y':
                print("Installation cancelled. Your local changes are preserved.")
                return False
    
    print("  Updating to clean state...")
    
    # Abort any in-progress operations
    git_operation(["merge", "--abort"])
    git_operation(["rebase", "--abort"])
    
    # Reset to clean state
    git_operation(["reset", "--hard", f"origin/{target_branch}"])
    git_operation(["clean", "-fd"])
    
    print("  [OK] Updated successfully to clean state")
    return True


def get_hook_command() -> str:
    """Get the appropriate hook command for the current platform"""
    if platform.system() == "Windows":
        # Use Python directly on Windows
        return f'python "{INSTALL_DIR}\\claude-docs-helper.py" hook-check'
    else:
        # Use shell script on Unix-like systems (for backward compatibility)
        # But also support Python version if shell script doesn't exist
        shell_script = INSTALL_DIR / "claude-docs-helper.sh"
        if shell_script.exists():
            return f'{INSTALL_DIR}/claude-docs-helper.sh hook-check'
        else:
            return f'python "{INSTALL_DIR}/claude-docs-helper.py" hook-check'


def setup_command_file():
    """Create or update the /docs command file"""
    print("Setting up /docs command...")
    
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    
    if COMMAND_FILE.exists():
        print("  Updating existing command...")
    
    # Create command content
    if platform.system() == "Windows":
        execute_cmd = f'python "{INSTALL_DIR}\\claude-docs-helper.py" "$ARGUMENTS"'
    else:
        # Check if shell script exists for backward compatibility
        shell_script = INSTALL_DIR / "claude-docs-helper.sh"
        if shell_script.exists():
            execute_cmd = f'{INSTALL_DIR}/claude-docs-helper.sh "$ARGUMENTS"'
        else:
            execute_cmd = f'python "{INSTALL_DIR}/claude-docs-helper.py" "$ARGUMENTS"'
    
    command_content = f'''Execute the Claude Code Docs helper script at {INSTALL_DIR}

Usage:
- /docs - List all available documentation topics
- /docs <topic> - Read specific documentation with link to official docs
- /docs -t - Check sync status without reading a doc
- /docs -t <topic> - Check freshness then read documentation
- /docs whats new - Show recent documentation changes (or "what's new")

Examples of expected output:

When reading a doc:
[INFO] COMMUNITY MIRROR: https://github.com/ericbuess/claude-code-docs
[INFO] OFFICIAL DOCS: https://docs.anthropic.com/en/docs/claude-code

[Doc content here...]

[INFO] Official page: https://docs.anthropic.com/en/docs/claude-code/hooks

When showing what's new:
[INFO] Recent documentation updates:

* 5 hours ago:
  Link: https://github.com/ericbuess/claude-code-docs/commit/eacd8e1
  Doc: data-usage: https://docs.anthropic.com/en/docs/claude-code/data-usage
     [+] Added: Privacy safeguards
  Doc: security: https://docs.anthropic.com/en/docs/claude-code/security
     [*] Data flow and dependencies section moved here

Full changelog: https://github.com/ericbuess/claude-code-docs/commits/main/docs
[INFO] COMMUNITY MIRROR - NOT AFFILIATED WITH ANTHROPIC

Every request checks for the latest documentation from GitHub (takes ~0.4s).
The helper script handles all functionality including auto-updates.

Execute: {execute_cmd}
'''
    
    COMMAND_FILE.write_text(command_content)
    print("[OK] Created /docs command")


def setup_hooks():
    """Setup automatic update hooks in Claude settings"""
    print("Setting up automatic updates...")
    
    hook_command = get_hook_command()
    
    # Ensure settings directory exists
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load or create settings
    if SETTINGS_FILE.exists():
        print("  Updating Claude settings...")
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            print("  [WARNING]  Warning: Invalid settings.json, creating new one")
            settings = {}
    else:
        print("  Creating Claude settings...")
        settings = {}
    
    # Initialize hooks structure
    if 'hooks' not in settings:
        settings['hooks'] = {}
    if 'PreToolUse' not in settings['hooks']:
        settings['hooks']['PreToolUse'] = []
    
    # Remove old claude-code-docs hooks
    pre_tool_use = settings['hooks']['PreToolUse']
    pre_tool_use[:] = [
        hook_entry for hook_entry in pre_tool_use
        if not any('claude-code-docs' in hook.get('command', '')
                  for hook in hook_entry.get('hooks', []))
    ]
    
    # Add new hook
    pre_tool_use.append({
        "matcher": "Read",
        "hooks": [{
            "type": "command",
            "command": hook_command
        }]
    })
    
    # Save settings
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("[OK] Updated Claude settings")


def setup_helper_script():
    """Create the Python helper script"""
    print("Installing helper script...")
    
    # Copy Python helper script from current directory if it exists
    source_helper = Path(__file__).parent / "claude-docs-helper.py"
    dest_helper = INSTALL_DIR / "claude-docs-helper.py"
    
    if source_helper.exists():
        shutil.copy(source_helper, dest_helper)
        print("[OK] Python helper script installed")
    
    # Copy uninstaller script
    source_uninstall = Path(__file__).parent / "uninstall.py"
    dest_uninstall = INSTALL_DIR / "uninstall.py"
    if source_uninstall.exists():
        shutil.copy(source_uninstall, dest_uninstall)
        print("[OK] Uninstaller script installed")
    
    # Also copy batch wrappers for Windows
    if platform.system() == "Windows":
        source_bat = Path(__file__).parent / "claude-docs-helper.bat"
        dest_bat = INSTALL_DIR / "claude-docs-helper.bat"
        if source_bat.exists():
            shutil.copy(source_bat, dest_bat)
            print("[OK] Windows batch wrapper installed")
        
        source_uninstall_bat = Path(__file__).parent / "uninstall.bat"
        dest_uninstall_bat = INSTALL_DIR / "uninstall.bat"
        if source_uninstall_bat.exists():
            shutil.copy(source_uninstall_bat, dest_uninstall_bat)
            print("[OK] Windows uninstall batch installed")
    
    # For backward compatibility, check if there's a shell template
    template_file = INSTALL_DIR / "scripts" / "claude-docs-helper.sh.template"
    shell_script = INSTALL_DIR / "claude-docs-helper.sh"
    
    # If shell template exists and we're on Unix, use it for backward compatibility
    if template_file.exists() and platform.system() != "Windows":
        shutil.copy(template_file, shell_script)
        # Make executable on Unix-like systems
        shell_script.chmod(0o755)
        print("[OK] Shell helper script installed (backward compatibility)")
    
    print("[OK] Helper script setup complete")


def cleanup_old_installations(old_installations: List[Path]):
    """Clean up old installations"""
    if not old_installations:
        return
    
    print()
    print("Cleaning up old installations...")
    print(f"Found {len(old_installations)} old installation(s) to remove:")
    
    for old_dir in old_installations:
        if not old_dir or not old_dir.exists():
            continue
        
        print(f"  - {old_dir}")
        
        # Check if it has uncommitted changes
        if (old_dir / ".git").exists():
            success, output = git_operation(["status", "--porcelain"], cwd=old_dir)
            if success and not output:
                try:
                    shutil.rmtree(old_dir)
                    print("    [OK] Removed (clean)")
                except Exception as e:
                    print(f"    [WARNING]  Could not remove: {e}")
            else:
                print("    [WARNING]  Preserved (has uncommitted changes)")
        else:
            print("    [WARNING]  Preserved (not a git repo)")


def list_available_topics():
    """List available documentation topics"""
    docs_dir = INSTALL_DIR / "docs"
    if docs_dir.exists():
        topics = sorted([f.stem for f in docs_dir.glob("*.md")])
        if topics:
            # Format topics in columns
            import textwrap
            wrapper = textwrap.TextWrapper(width=60)
            topic_str = "  ".join(topics)
            wrapped = wrapper.wrap(topic_str)
            for line in wrapped:
                print(line)


def main():
    """Main installation logic"""
    print_header()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Find existing installations before any changes
    existing_installs = find_existing_installations()
    
    if existing_installs:
        print(f"Found {len(existing_installs)} existing installation(s):")
        for install in existing_installs:
            print(f"  - {install}")
        print()
    
    # Check if already installed at new location
    if INSTALL_DIR.exists() and (INSTALL_DIR / "docs" / "docs_manifest.json").exists():
        print("[OK] Found installation at ~/.claude-code-docs")
        print("  Updating to latest version...")
        
        if not safe_git_update():
            print("[ERROR] Update failed")
            sys.exit(1)
    else:
        # Need to install at new location
        if existing_installs:
            # Migrate from old location
            migrate_installation(existing_installs[0])
        else:
            # Fresh installation
            print("No existing installation found")
            print("Installing fresh to ~/.claude-code-docs...")
            
            success, output = git_operation(["clone", "-b", INSTALL_BRANCH, REPO_URL, str(INSTALL_DIR)])
            if not success:
                print(f"[ERROR] Failed to clone repository: {output}")
                sys.exit(1)
    
    print()
    print(f"Setting up Claude Code Docs v{VERSION}...")
    
    # Setup components
    setup_helper_script()
    setup_command_file()
    setup_hooks()
    
    # Clean up old installations
    cleanup_old_installations(existing_installs)
    
    # Success message
    print()
    print(f"[SUCCESS] Claude Code Docs v{VERSION} installed successfully!")
    print()
    print("[INFO] Command: /docs (user)")
    print(f"[INFO] Location: {INSTALL_DIR}")
    print()
    print("Usage examples:")
    print("  /docs hooks         # Read hooks documentation")
    print("  /docs -t           # Check when docs were last updated")
    print("  /docs what's new   # See recent documentation changes")
    print()
    print("[INFO] Auto-updates: Enabled - syncs automatically when GitHub has newer content")
    print()
    print("Available topics:")
    list_available_topics()
    print()
    print("[WARNING]  Note: Restart Claude Code for auto-updates to take effect")
    
    # Platform-specific notes
    if platform.system() == "Windows":
        print()
        print("[INFO] Windows-specific notes:")
        print("  - Python must be in your PATH for hooks to work")
        print("  - If you have issues, try running: python -m pip install requests")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Installation failed: {e}")
        sys.exit(1)