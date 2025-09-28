#!/usr/bin/env python3
"""
Fix Unicode emoji characters in Python files to prevent encoding errors on Windows
"""

import os
import glob
import re

def fix_unicode_in_file(file_path):
    """Replace common Unicode emoji characters with ASCII equivalents"""
    
    unicode_replacements = {
        '✅': '[OK]',
        '⚠️': '[WARNING]',
        '❌': '[ERROR]',
        '🚀': '[ROCKET]',
        '🛒': '[CART]',
        '🌐': '[GLOBE]',
        '🔥': '[FIRE]',
        '💡': '[BULB]',
        '📁': '[FOLDER]',
        '📱': '[PHONE]',
        '💻': '[LAPTOP]',
        '🎯': '[TARGET]',
        '⭐': '[STAR]',
        '🎨': '[ART]',
        '🧠': '[BRAIN]',
        '👤': '[USER]',
        '📧': '[EMAIL]',
        '📄': '[DOCUMENT]',
        '⚡': '[LIGHTNING]',
        '🔧': '[WRENCH]',
        '🎬': '[MOVIE]',
        '📊': '[CHART]',
        '🎵': '[MUSIC]',
        '🔐': '[LOCK]',
        '⏰': '[CLOCK]',
        '📦': '[PACKAGE]',
        '🎪': '[CIRCUS]',
        '🪙': '[COIN]',
        '💰': '[MONEY]',
        '💎': '[DIAMOND]',
        '🏆': '[TROPHY]',
        '📈': '[TRENDING_UP]',
        '📉': '[TRENDING_DOWN]',
        '🌟': '[SPARKLE]',
        '✨': '[SPARKLES]'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each Unicode character with ASCII equivalent
        for unicode_char, ascii_replacement in unicode_replacements.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed Unicode characters in: {file_path}")
            return True
        else:
            print(f"No Unicode characters found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix Unicode characters in all Python files in the apps/api directory"""
    
    base_dir = os.path.join(os.path.dirname(__file__), 'apps', 'api')
    python_files = glob.glob(os.path.join(base_dir, '*.py'))
    
    print(f"Fixing Unicode characters in {len(python_files)} Python files...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_unicode_in_file(file_path):
            fixed_count += 1
    
    print(f"\nCompleted! Fixed {fixed_count} files.")

if __name__ == '__main__':
    main()