import os
import re
from pathlib import Path

# Pattern sucht nach: class X:\n    """\n    def __getstate__
# Das """ vor def __getstate__ ist falsch platziert
pattern = re.compile(
    r'(class \w+:\s*\n\s*)"""(\s*\n\s*def __getstate__\(\self\):\s*\n\s*""")',
    re.MULTILINE
)

# Alternative Pattern für bereits teilweise korrigierte
pattern2 = re.compile(
    r'(class \w+:\s*\n\s*)"""(\s*\n\s*def __getstate__)',
    re.MULTILINE  
)

fixed_files = []
core_path = Path('core')

for py_file in core_path.glob('*.py'):
    try:
        content = py_file.read_text(encoding='utf-8')
        original = content
        
        # Versuche beide Patterns
        content = pattern.sub(r'\1\2', content)
        content = pattern2.sub(r'\1\2', content)
        
        if content != original:
            py_file.write_text(content, encoding='utf-8')
            fixed_files.append(str(py_file))
            
    except Exception as e:
        print(f'Error in {py_file}: {e}')

print(f'\nFixed {len(fixed_files)} files:')
for f in fixed_files:
    print(f'  ✓ {f}')

if not fixed_files:
    print('No files needed fixing!')
