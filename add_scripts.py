#!/usr/bin/env python3
"""
Add API scripts to all HTML files
"""

import os
import re

def add_scripts_to_html(file_path):
    """Add API scripts to HTML file if not already present"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if scripts are already present
    if 'js/api.js' in content and 'js/auth.js' in content and 'js/init.js' in content:
        print(f"✅ {file_path} - Scripts already present")
        return
    
    # Find the head tag
    head_pattern = r'(<head[^>]*>)'
    head_match = re.search(head_pattern, content, re.IGNORECASE)
    
    if head_match:
        head_start = head_match.start()
        head_end = head_match.end()
        
        # Find the closing head tag
        head_close_pattern = r'(</head>)'
        head_close_match = re.search(head_close_pattern, content, re.IGNORECASE)
        
        if head_close_match:
            # Insert scripts before closing head tag
            scripts = '\n    <script src="js/api.js"></script>\n    <script src="js/auth.js"></script>\n    <script src="js/init.js"></script>\n'
            
            new_content = content[:head_close_match.start()] + scripts + content[head_close_match.start():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ {file_path} - Scripts added")
        else:
            print(f"❌ {file_path} - No closing head tag found")
    else:
        print(f"❌ {file_path} - No head tag found")

def main():
    """Add scripts to all HTML files"""
    html_files = [
        'frontend/Aztec/settings.html',
        'frontend/Aztec/analytics.html',
        'frontend/Aztec/history.html'
    ]
    
    for file_path in html_files:
        if os.path.exists(file_path):
            add_scripts_to_html(file_path)
        else:
            print(f"❌ {file_path} - File not found")

if __name__ == "__main__":
    main() 