#!/usr/bin/env python3
"""
EduPlan AI - Project Structure Summary
Shows the current organized folder structure
"""

import os
from pathlib import Path

def show_tree_structure(path, prefix="", max_depth=3, current_depth=0):
    """Display directory tree structure"""
    if current_depth >= max_depth:
        return
    
    items = sorted(Path(path).iterdir())
    dirs = [item for item in items if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__']
    files = [item for item in items if item.is_file() and not item.name.startswith('.') and not item.name.endswith('.pyc')]
    
    # Show directories first
    for i, item in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and len(files) == 0
        connector = "└── " if is_last_dir else "├── "
        print(f"{prefix}{connector}📁 {item.name}/")
        
        extension = "    " if is_last_dir else "│   "
        show_tree_structure(item, prefix + extension, max_depth, current_depth + 1)
    
    # Show files
    for i, item in enumerate(files):
        is_last = i == len(files) - 1
        connector = "└── " if is_last else "├── "
        
        # Add emoji based on file type
        if item.suffix == '.py':
            emoji = "🐍"
        elif item.suffix == '.json':
            emoji = "📄"
        elif item.suffix == '.md':
            emoji = "📖"
        elif item.suffix == '.txt':
            emoji = "📝"
        elif item.suffix == '.pdf':
            emoji = "📕"
        else:
            emoji = "📄"
            
        print(f"{prefix}{connector}{emoji} {item.name}")

def main():
    """Show project structure"""
    print("🏗️  EduPlan AI - Organized Project Structure")
    print("=" * 50)
    print("📁 EduPlan_AI/")
    
    project_root = Path(".")
    show_tree_structure(project_root, "")
    
    print("\n📊 Project Statistics:")
    print("-" * 25)
    
    # Count files by type
    py_files = list(project_root.rglob("*.py"))
    json_files = list(project_root.rglob("*.json"))
    md_files = list(project_root.rglob("*.md"))
    
    print(f"🐍 Python files: {len(py_files)}")
    print(f"📄 JSON files: {len(json_files)}")
    print(f"📖 Markdown files: {len(md_files)}")
    
    # Key directories info
    print(f"\n🎯 Key Components:")
    print(f"  • Main entry point: main.py")
    print(f"  • Core modules: src/")
    print(f"  • Scripts: scripts/")
    print(f"  • Data: data/")
    print(f"  • Outputs: outputs/")
    print(f"  • Documentation: docs/")

if __name__ == "__main__":
    main()
