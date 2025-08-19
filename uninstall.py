#!/usr/bin/env python3
"""
Claude Code Docs Uninstaller - Cross-platform uninstallation
Removes all Claude Code Docs components cleanly
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Fix Windows console encoding for Unicode
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
HOME = Path.home()
INSTALL_DIR = HOME / ".claude-code-docs"
CLAUDE_DIR = HOME / ".claude"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
COMMAND_FILE = CLAUDE_DIR / "commands" / "docs.md"


def print_header():
    """Print uninstaller header"""
    print("Claude Code Documentation Mirror - Uninstaller")
    print("=" * 46)
    print()


def find_all_installations() -> List[Path]:
    """Find all claude-code-docs installations"""
    installations = []
    
    # Check command file for paths
    if COMMAND_FILE.exists():
        try:
            content = COMMAND_FILE.read_text()
            import re
            # Look for execution paths
            matches = re.findall(r'["\']?([^"\']*claude-code-docs[^"\']*)["\'\\]', content)
            for match in matches:
                # Clean up the path
                path_str = match.replace('\\', os.sep).replace('/', os.sep)
                if 'claude-docs-helper' in path_str:
                    # Extract just the directory part
                    path_str = path_str.split('claude-docs-helper')[0].rstrip(os.sep)
                
                path = Path(path_str.replace('~', str(HOME)))
                if path.exists() and path.is_dir():
                    installations.append(path)
        except Exception:
            pass
    
    # Check settings.json hooks
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            
            hooks = settings.get('hooks', {}).get('PreToolUse', [])
            for hook_entry in hooks:
                for hook in hook_entry.get('hooks', []):
                    command = hook.get('command', '')
                    if 'claude-code-docs' in command:
                        import re
                        matches = re.findall(r'["\']?([^"\']*claude-code-docs[^"\']*)["\'\\]', command)
                        for match in matches:
                            path_str = match.replace('\\', os.sep).replace('/', os.sep)
                            if 'claude-docs-helper' in path_str:
                                path_str = path_str.split('claude-docs-helper')[0].rstrip(os.sep)
                            
                            path = Path(path_str.replace('~', str(HOME)))
                            if path.exists() and path.is_dir():
                                installations.append(path)
        except Exception:
            pass
    
    # Add standard installation location
    if INSTALL_DIR.exists():
        installations.append(INSTALL_DIR)
    
    # Deduplicate
    unique_installations = []
    for path in installations:
        if path not in unique_installations:
            unique_installations.append(path)
    
    return unique_installations


def git_operation(args: List[str], cwd: Path) -> Tuple[bool, str]:
    """Execute git operation"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, ""


def remove_command_file():
    """Remove the /docs command file"""
    if COMMAND_FILE.exists():
        try:
            COMMAND_FILE.unlink()
            print("[OK] Removed /docs command")
            return True
        except Exception as e:
            print(f"[WARNING] Could not remove command file: {e}")
            return False
    return True


def remove_hooks():
    """Remove claude-code-docs hooks from settings"""
    if not SETTINGS_FILE.exists():
        return True
    
    try:
        # Backup settings first
        backup_file = SETTINGS_FILE.with_suffix('.json.backup')
        shutil.copy2(SETTINGS_FILE, backup_file)
        
        # Load settings
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        
        # Remove hooks containing claude-code-docs
        if 'hooks' in settings and 'PreToolUse' in settings['hooks']:
            original_count = len(settings['hooks']['PreToolUse'])
            settings['hooks']['PreToolUse'] = [
                hook_entry for hook_entry in settings['hooks']['PreToolUse']
                if not any('claude-code-docs' in hook.get('command', '')
                          for hook in hook_entry.get('hooks', []))
            ]
            removed_count = original_count - len(settings['hooks']['PreToolUse'])
            
            # Clean up empty structures
            if not settings['hooks']['PreToolUse']:
                del settings['hooks']['PreToolUse']
            if 'hooks' in settings and not settings['hooks']:
                del settings['hooks']
            
            # Save updated settings
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            
            if removed_count > 0:
                print(f"[OK] Removed {removed_count} hook(s) (backup: {backup_file})")
            else:
                print("[OK] No hooks to remove")
            return True
            
    except Exception as e:
        print(f"[WARNING] Could not remove hooks: {e}")
        return False


def remove_directories(installations: List[Path]):
    """Remove installation directories"""
    if not installations:
        return
    
    print()
    for path in installations:
        if not path.exists():
            continue
        
        # Check if it's a git repository with uncommitted changes
        has_changes = False
        if (path / ".git").exists():
            success, output = git_operation(["status", "--porcelain"], cwd=path)
            has_changes = bool(output) if success else False
        
        if has_changes:
            print(f"[WARNING] Preserved {path} (has uncommitted changes)")
        else:
            try:
                shutil.rmtree(path)
                print(f"[OK] Removed {path}")
            except Exception as e:
                print(f"[WARNING] Could not remove {path}: {e}")


def main():
    """Main uninstall logic"""
    print_header()
    
    # Find all installations
    installations = find_all_installations()
    
    if installations:
        print("Found installations at:")
        for path in installations:
            print(f"  [DIR] {path}")
        print()
    
    print("This will remove:")
    print("  * The /docs command from ~/.claude/commands/docs.md")
    print("  * All claude-code-docs hooks from ~/.claude/settings.json")
    if installations:
        print("  • Installation directories (if safe to remove)")
    print()
    
    # Confirm with user
    try:
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    print()
    
    # Perform uninstallation
    success = True
    
    # Remove command file
    if not remove_command_file():
        success = False
    
    # Remove hooks
    if not remove_hooks():
        success = False
    
    # Remove directories
    remove_directories(installations)
    
    # Final message
    print()
    if success:
        print("[SUCCESS] Uninstall complete!")
    else:
        print("[WARNING] Uninstall completed with warnings")
    
    print()
    print("To reinstall:")
    if platform.system() == "Windows":
        print('curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py -o install.py && python install.py')
    else:
        print('curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.sh | bash')
        print('# or use Python installer:')
        print('python <(curl -fsSL https://raw.githubusercontent.com/ericbuess/claude-code-docs/main/install.py)')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Uninstall failed: {e}")
        sys.exit(1)