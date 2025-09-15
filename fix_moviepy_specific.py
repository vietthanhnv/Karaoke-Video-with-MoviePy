#!/usr/bin/env python3
"""
Precise MoviePy v2 Compatibility Fixer

This script only fixes actual MoviePy method calls, not GUI or other library methods.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict

def find_moviepy_files() -> List[Path]:
    """Find files that actually use MoviePy."""
    moviepy_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'moviepy_repo']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Only include files that actually import or use MoviePy
                    if any(pattern in content for pattern in [
                        'from moviepy import',
                        'import moviepy',
                        'moviepy.',
                        'AudioFileClip',
                        'VideoFileClip',
                        'TextClip',
                        'CompositeVideoClip',
                        'ColorClip',
                        'ImageClip'
                    ]):
                        moviepy_files.append(filepath)
                except:
                    continue
    
    return moviepy_files

def fix_moviepy_methods(content: str) -> tuple[str, List[str]]:
    """Fix actual MoviePy method calls."""
    fixes = []
    
    # Only fix methods when they're clearly on MoviePy objects
    # Look for patterns like: clip.set_duration, audio_clip.set_start, etc.
    
    # Pattern 1: variable_name.method_call where variable suggests MoviePy
    moviepy_var_patterns = [
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.set_duration\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.set_position\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.set_start\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.set_end\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.set_fps\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.resize\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.crop\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.rotate\(',
        r'(\w*clip\w*|audio|video|text_clip|preview_clip|background_clip)\.subclip\(',
    ]
    
    replacements = {
        'set_duration': 'with_duration',
        'set_position': 'with_position',
        'set_start': 'with_start',
        'set_end': 'with_end',
        'set_fps': 'with_fps',
        'resize': 'resized',
        'crop': 'cropped',
        'rotate': 'rotated',
        'subclip': 'subclipped',
    }
    
    for pattern in moviepy_var_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            old_method = None
            for old, new in replacements.items():
                if f'.{old}(' in match.group():
                    old_method = old
                    new_method = new
                    break
            
            if old_method:
                old_call = match.group()
                new_call = old_call.replace(f'.{old_method}(', f'.{new_method}(')
                content = content.replace(old_call, new_call)
                fixes.append(f"Fixed: {old_call} → {new_call}")
    
    # Fix crossfade methods
    crossfade_patterns = [
        (r'(\w*clip\w*)\.crossfadein\(([^)]+)\)', r'\1.with_effects([vfx.CrossFadeIn(\2)])'),
        (r'(\w*clip\w*)\.crossfadeout\(([^)]+)\)', r'\1.with_effects([vfx.CrossFadeOut(\2)])')
    ]
    
    for pattern, replacement in crossfade_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes.append(f"Fixed crossfade: {pattern} → {replacement}")
    
    # Fix TextClip parameters
    textclip_fixes = [
        (r'TextClip\(([^)]*?)fontsize\s*=', r'TextClip(\1font_size='),
        (r'TextClip\(([^)]*?)txt\s*=', r'TextClip(\1text=')
    ]
    
    for pattern, replacement in textclip_fixes:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes.append(f"Fixed TextClip parameter: {pattern} → {replacement}")
    
    return content, fixes

def main():
    """Main function."""
    print("🎬 Precise MoviePy v2 Compatibility Fixer")
    print("=" * 50)
    
    dry_run = '--fix' not in sys.argv
    
    if dry_run:
        print("🔍 Running in CHECK mode (use --fix to apply changes)")
    else:
        print("🔧 Running in FIX mode - will modify files!")
    
    moviepy_files = find_moviepy_files()
    print(f"\n📊 Found {len(moviepy_files)} files that use MoviePy")
    
    total_fixes = 0
    files_fixed = 0
    
    for filepath in moviepy_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, fixes = fix_moviepy_methods(content)
            
            if fixes:
                print(f"\n📁 {filepath}")
                for fix in fixes:
                    print(f"  ✅ {fix}")
                
                total_fixes += len(fixes)
                files_fixed += 1
                
                if not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  💾 File updated")
        
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
    
    print(f"\n📈 Summary:")
    print(f"   MoviePy files: {len(moviepy_files)}")
    print(f"   Files with fixes: {files_fixed}")
    print(f"   Total fixes: {total_fixes}")
    
    if total_fixes == 0:
        print("🎉 No MoviePy v2 compatibility issues found!")
    elif dry_run:
        print(f"\n💡 Run with --fix to apply these fixes")
    else:
        print(f"✅ All MoviePy issues fixed!")

if __name__ == "__main__":
    main()