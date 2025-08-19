#!/usr/bin/env python3
"""
Claude Code Docs Helper - Cross-platform documentation access
Provides local documentation reading with auto-update capabilities
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Fix Windows console encoding for Unicode
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
INSTALL_DIR = Path(__file__).parent.resolve()
DOCS_DIR = INSTALL_DIR / "docs"
MANIFEST_FILE = DOCS_DIR / "docs_manifest.json"
LAST_CHECK_FILE = INSTALL_DIR / ".last_check"
CHECK_INTERVAL = timedelta(hours=3)  # Check for updates every 3 hours
GITHUB_REPO = "https://github.com/ericbuess/claude-code-docs"
OFFICIAL_DOCS = "https://docs.anthropic.com/en/docs/claude-code"


def load_manifest() -> Dict:
    """Load the documentation manifest"""
    if not MANIFEST_FILE.exists():
        return {}
    
    try:
        with open(MANIFEST_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def git_operation(args: List[str]) -> Tuple[bool, str]:
    """Execute git operation"""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=INSTALL_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "Git not found"


def check_for_updates() -> Tuple[bool, str]:
    """Check if there are updates available from GitHub"""
    # Fetch from remote
    success, output = git_operation(["fetch", "--quiet"])
    if not success:
        return False, "Could not check for updates"
    
    # Check if we're behind remote
    success, behind = git_operation(["rev-list", "--count", "HEAD..origin/main"])
    if not success:
        return False, "Could not compare with remote"
    
    behind_count = int(behind) if behind.isdigit() else 0
    
    if behind_count > 0:
        return True, f"{behind_count} update(s) available"
    else:
        return False, "Already up to date"


def pull_updates() -> bool:
    """Pull latest updates from GitHub"""
    print("[UPDATE] Updating documentation...")
    success, output = git_operation(["pull", "--quiet"])
    
    if success:
        print("[OK] Documentation updated successfully")
        return True
    else:
        print(f"[WARNING]  Update failed: {output}")
        return False


def get_last_update_time() -> Optional[datetime]:
    """Get the last time docs were updated"""
    success, output = git_operation(["log", "-1", "--format=%ct", "docs/"])
    if success and output.isdigit():
        return datetime.fromtimestamp(int(output))
    return None


def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X hours/days ago'"""
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"


def list_topics() -> List[str]:
    """List all available documentation topics"""
    if not DOCS_DIR.exists():
        return []
    
    topics = []
    for file in sorted(DOCS_DIR.glob("*.md")):
        topics.append(file.stem)
    
    return topics


def read_doc(topic: str) -> Optional[str]:
    """Read a specific documentation file"""
    # Try exact match first
    doc_file = DOCS_DIR / f"{topic}.md"
    
    if not doc_file.exists():
        # Try case-insensitive match
        for file in DOCS_DIR.glob("*.md"):
            if file.stem.lower() == topic.lower():
                doc_file = file
                break
    
    if not doc_file.exists():
        # Try partial match
        for file in DOCS_DIR.glob("*.md"):
            if topic.lower() in file.stem.lower():
                doc_file = file
                break
    
    if doc_file.exists():
        try:
            return doc_file.read_text(encoding='utf-8')
        except Exception as e:
            return f"Error reading file: {e}"
    
    return None


def show_whats_new(limit: int = 5) -> None:
    """Show recent documentation changes"""
    print("[INFO] Recent documentation updates:")
    print()
    
    # Get recent commits
    success, output = git_operation([
        "log", "--pretty=format:%H|%ct|%s", 
        f"-{limit}", "docs/"
    ])
    
    if not success:
        print("Could not retrieve recent changes")
        return
    
    if not output:
        print("No recent changes found")
        return
    
    for line in output.splitlines():
        parts = line.split('|', 2)
        if len(parts) >= 3:
            commit_hash = parts[0][:7]
            timestamp = int(parts[1])
            message = parts[2]
            
            dt = datetime.fromtimestamp(timestamp)
            time_ago = format_time_ago(dt)
            
            print(f"* {time_ago}:")
            print(f"  Link: {GITHUB_REPO}/commit/{commit_hash}")
            
            # Try to extract file changes from commit message
            if "Updated:" in message or "Added:" in message:
                changes = message.split("Updated:")[-1].split("Added:")[-1].strip()
                for change in changes.split(','):
                    change = change.strip()
                    if change:
                        doc_name = change.replace('.md', '')
                        print(f"  Doc: {doc_name}: {OFFICIAL_DOCS}/{doc_name}")
            print()
    
    print(f"Link: Full changelog: {GITHUB_REPO}/commits/main/docs")
    print("[INFO] COMMUNITY MIRROR - NOT AFFILIATED WITH ANTHROPIC")


def check_freshness() -> None:
    """Check and display documentation freshness"""
    last_update = get_last_update_time()
    
    if last_update:
        time_ago = format_time_ago(last_update)
        print(f"[INFO] Docs last updated: {time_ago}")
    else:
        print("[INFO] Could not determine last update time")
    
    # Check for available updates
    has_updates, message = check_for_updates()
    
    if has_updates:
        print(f"[UPDATE] {message}")
        pull_updates()
    else:
        print(f"[OK] {message}")
    
    print()


def hook_check() -> None:
    """Called by Claude Code hooks to auto-update when needed"""
    # Check if enough time has passed since last check
    should_check = True
    
    if LAST_CHECK_FILE.exists():
        try:
            last_check_time = datetime.fromtimestamp(LAST_CHECK_FILE.stat().st_mtime)
            if datetime.now() - last_check_time < CHECK_INTERVAL:
                should_check = False
        except Exception:
            pass
    
    if should_check:
        # Update last check time
        LAST_CHECK_FILE.touch()
        
        # Check for updates silently
        has_updates, _ = check_for_updates()
        if has_updates:
            pull_updates()


def main():
    """Main entry point"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Handle hook check (called by Claude Code)
    if args and args[0] == "hook-check":
        hook_check()
        return
    
    # Handle uninstall info
    if args and args[0] == "uninstall":
        print("To uninstall Claude Code Docs, run:")
        print()
        if os.name == 'nt':  # Windows
            print(f'python "{INSTALL_DIR}\\uninstall.py"')
        else:
            uninstall_script = INSTALL_DIR / "uninstall.sh"
            if uninstall_script.exists():
                print(f'{uninstall_script}')
            else:
                print(f'python "{INSTALL_DIR}/uninstall.py"')
        return
    
    # Handle freshness check flag
    check_fresh = False
    if args and args[0] == "-t":
        check_fresh = True
        args = args[1:]  # Remove the flag from args
    
    # No arguments - list topics
    if not args:
        if check_fresh:
            check_freshness()
        
        print("[INFO] COMMUNITY MIRROR: " + GITHUB_REPO)
        print("[INFO] OFFICIAL DOCS: " + OFFICIAL_DOCS)
        print()
        print("Available documentation topics:")
        print()
        
        topics = list_topics()
        if topics:
            # Format in columns
            import textwrap
            wrapper = textwrap.TextWrapper(width=60, initial_indent="  ", subsequent_indent="  ")
            topic_str = "  ".join(topics)
            wrapped = wrapper.wrap(topic_str)
            for line in wrapped:
                print(line)
        else:
            print("  No documentation files found")
        
        print()
        print("Usage: /docs <topic>")
        print("       /docs -t         # Check sync status")
        print("       /docs what's new # Show recent changes")
        
        if not check_fresh:
            print()
            print("[INFO] Reading from local docs (run /docs -t to check freshness)")
        return
    
    # Handle "what's new" or "whats new"
    full_arg = " ".join(args).lower()
    if full_arg in ["what's new", "whats new", "what is new", "changelog"]:
        if check_fresh:
            check_freshness()
        show_whats_new()
        return
    
    # Read specific documentation
    topic = args[0]
    
    if check_fresh:
        check_freshness()
    
    print("[INFO] COMMUNITY MIRROR: " + GITHUB_REPO)
    print("[INFO] OFFICIAL DOCS: " + OFFICIAL_DOCS)
    print()
    
    content = read_doc(topic)
    
    if content:
        print(content)
        print()
        print(f"[INFO] Official page: {OFFICIAL_DOCS}/{topic}")
    else:
        print(f"[ERROR] Documentation for '{topic}' not found")
        print()
        print("Available topics:")
        topics = list_topics()
        if topics:
            # Show similar topics
            similar = [t for t in topics if topic.lower() in t.lower() or t.lower() in topic.lower()]
            if similar:
                print("  Similar topics:")
                for t in similar[:5]:
                    print(f"    - {t}")
            else:
                # Show first few topics
                for t in topics[:10]:
                    print(f"  - {t}")
                if len(topics) > 10:
                    print(f"  ... and {len(topics) - 10} more")
    
    if not check_fresh:
        print()
        print("[INFO] Reading from local docs (run /docs -t to check freshness)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)