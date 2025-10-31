"""Script to indent the solar_3d_view.py file content into the function"""

with open('pages/solar_3d_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by the function definition
parts = content.split('def _render_3d_view_impl():')
if len(parts) != 2:
    print("Error: Could not find function definition")
    exit(1)

before = parts[0]
after = parts[1]

# Find the end of the docstring and comments
lines = after.split('\n')
new_lines = []
found_code_start = False
docstring_count = 0

for line in lines:
    # Keep function signature line and docstring as is
    if '"""' in line:
        docstring_count += 1
        new_lines.append(line)
        if docstring_count == 2:
            found_code_start = True
        continue
    
    if not found_code_start:
        new_lines.append(line)
        continue
    
    # Now indent the actual code
    if line.strip():  # Non-empty line
        if not line.startswith('    '):  # Not already indented
            new_lines.append('    ' + line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

# Reconstruct the file
new_content = before + 'def _render_3d_view_impl():\n' + '\n'.join(new_lines)

# Add function call at the end if running as main
if '__name__' not in new_content:
    new_content += '\n\n# When run as standalone page\nif __name__ == "__main__":\n    render_3d_view()\n'

with open('pages/solar_3d_view.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("File indented successfully")
