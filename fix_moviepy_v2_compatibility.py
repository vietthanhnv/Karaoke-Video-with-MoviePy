#!/usr/bin/env python3
"""
MoviePy v2 Compatibility Checker and Fixer

This script checks all MoviePy usage in the codebase and ensures compatibility
with MoviePy v2 API changes based on the official migration guide.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'moviepy_repo']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def check_moviepy_imports(content: str, filepath: Path) -> List[Dict]:
    """Check for MoviePy import patterns and suggest fixes."""
    issues = []
    
    # Check for old moviepy.editor imports
    if 'from moviepy.editor import' in content:
        issues.append({
            'type': 'import',
            'issue': 'Using deprecated moviepy.editor import',
            'suggestion': 'Use "from moviepy import ..." instead',
            'pattern': r'from moviepy\.editor import.*',
            'replacement': 'from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip, vfx, afx'
        })
    
    return issues

def check_method_calls(content: str, filepath: Path) -> List[Dict]:
    """Check for old MoviePy v1 method calls."""
    issues = []
    
    # Method name changes
    method_changes = {
        r'\.set_duration\(': '.with_duration(',
        r'\.set_position\(': '.with_position(',
        r'\.set_start\(': '.with_start(',
        r'\.set_end\(': '.with_end(',
        r'\.set_fps\(': '.with_fps(',
        r'\.resize\(': '.resized(',
        r'\.crop\(': '.cropped(',
        r'\.rotate\(': '.rotated(',
        r'\.subclip\(': '.subclipped(',
    }
    
    for old_pattern, new_method in method_changes.items():
        if re.search(old_pattern, content):
            issues.append({
                'type': 'method',
                'issue': f'Using deprecated method {old_pattern}',
                'suggestion': f'Use {new_method} instead',
                'pattern': old_pattern,
                'replacement': new_method
            })
    
    # Effects changes
    if re.search(r'\.crossfadein\(', content):
        issues.append({
            'type': 'effect',
            'issue': 'Using deprecated .crossfadein() method',
            'suggestion': 'Use .with_effects([vfx.CrossFadeIn(duration)]) instead',
            'pattern': r'\.crossfadein\(([^)]+)\)',
            'replacement': r'.with_effects([vfx.CrossFadeIn(\1)])'
        })
    
    if re.search(r'\.crossfadeout\(', content):
        issues.append({
            'type': 'effect',
            'issue': 'Using deprecated .crossfadeout() method',
            'suggestion': 'Use .with_effects([vfx.CrossFadeOut(duration)]) instead',
            'pattern': r'\.crossfadeout\(([^)]+)\)',
            'replacement': r'.with_effects([vfx.CrossFadeOut(\1)])'
        })
    
    return issues

def check_textclip_params(content: str, filepath: Path) -> List[Dict]:
    """Check for old TextClip parameter names."""
    issues = []
    
    # TextClip parameter changes
    if re.search(r'TextClip\([^)]*fontsize\s*=', content):
        issues.append({
            'type': 'parameter',
            'issue': 'Using deprecated fontsize parameter in TextClip',
            'suggestion': 'Use font_size instead of fontsize',
            'pattern': r'fontsize\s*=',
            'replacement': 'font_size='
        })
    
    if re.search(r'TextClip\([^)]*txt\s*=', content):
        issues.append({
            'type': 'parameter',
            'issue': 'Using deprecated txt parameter in TextClip',
            'suggestion': 'Use text instead of txt',
            'pattern': r'txt\s*=',
            'replacement': 'text='
        })
    
    return issues

def analyze_file(filepath: Path) -> Dict:
    """Analyze a single Python file for MoviePy compatibility issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'filepath': filepath, 'error': str(e), 'issues': []}
    
    issues = []
    issues.extend(check_moviepy_imports(content, filepath))
    issues.extend(check_method_calls(content, filepath))
    issues.extend(check_textclip_params(content, filepath))
    
    return {
        'filepath': filepath,
        'content': content,
        'issues': issues
    }

def fix_file(analysis: Dict, dry_run: bool = True) -> bool:
    """Fix MoviePy compatibility issues in a file."""
    if not analysis['issues']:
        return False
    
    content = analysis['content']
    filepath = analysis['filepath']
    
    print(f"\n📁 {filepath}")
    
    for issue in analysis['issues']:
        print(f"  ⚠️  {issue['issue']}")
        print(f"     💡 {issue['suggestion']}")
        
        if not dry_run:
            # Apply the fix
            content = re.sub(issue['pattern'], issue['replacement'], content)
            print(f"     ✅ Fixed!")
        else:
            print(f"     🔍 Would fix: {issue['pattern']} → {issue['replacement']}")
    
    if not dry_run:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ File updated successfully")
            return True
        except Exception as e:
            print(f"  ❌ Error writing file: {e}")
            return False
    
    return True

def main():
    """Main function to check and fix MoviePy compatibility."""
    print("🎬 MoviePy v2 Compatibility Checker and Fixer")
    print("=" * 50)
    
    # Check if we should run in fix mode
    dry_run = '--fix' not in sys.argv
    
    if dry_run:
        print("🔍 Running in CHECK mode (use --fix to apply changes)")
    else:
        print("🔧 Running in FIX mode - will modify files!")
    
    # Find all Python files
    python_files = find_python_files('.')
    print(f"\n📊 Found {len(python_files)} Python files to analyze")
    
    # Analyze files
    total_issues = 0
    files_with_issues = 0
    
    for filepath in python_files:
        analysis = analyze_file(filepath)
        
        if analysis.get('error'):
            print(f"❌ Error analyzing {filepath}: {analysis['error']}")
            continue
        
        if analysis['issues']:
            files_with_issues += 1
            total_issues += len(analysis['issues'])
            fix_file(analysis, dry_run)
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"   Files analyzed: {len(python_files)}")
    print(f"   Files with issues: {files_with_issues}")
    print(f"   Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("🎉 No MoviePy v2 compatibility issues found!")
    elif dry_run:
        print(f"\n💡 Run with --fix to automatically fix these issues")
    else:
        print(f"✅ All issues have been fixed!")
    
    # Test MoviePy imports
    print(f"\n🧪 Testing MoviePy imports...")
    try:
        from moviepy import VideoClip, TextClip, CompositeVideoClip, vfx, afx, AudioFileClip
        print("✅ All MoviePy v2 imports successful!")
    except ImportError as e:
        print(f"❌ MoviePy import error: {e}")
    except Exception as e:
        print(f"⚠️  MoviePy import warning: {e}")

if __name__ == "__main__":
    main()