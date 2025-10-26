#!/usr/bin/env python3
"""
Behebt Streamlit Deprecation Warnings automatisch
"""
import glob
import os
import re


def fix_streamlit_deprecations(directory="."):
    """Behebt bekannte Streamlit Deprecations"""

    fixes = {
        # use_column_width -> use_container_width
        r'use_column_width\s*=\s*True': 'use_container_width=True',
        r'use_column_width\s*=\s*False': 'use_container_width=False',

        # beta_columns -> columns
        r'st\.beta_columns\s*\(': 'st.columns(',

        # beta_container -> container
        r'st\.beta_container\s*\(': 'st.container(',

        # Legacy cache -> new cache
        r'@st\.cache\b': '@st.cache_data',
    }

    fixed_files = 0
    total_fixes = 0

    for file_path in glob.glob(os.path.join(directory, "*.py")):
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            for old_pattern, new_replacement in fixes.items():
                matches = len(re.findall(old_pattern, content))
                if matches > 0:
                    content = re.sub(old_pattern, new_replacement, content)
                    file_fixes += matches
                    print(
                        f"  ✅ {matches}x '{old_pattern}' -> '{new_replacement}'")

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files += 1
                total_fixes += file_fixes
                print(f"🔧 {os.path.basename(file_path)}: {file_fixes} Fixes")

        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")

    print(f"\n🎉 {fixed_files} Dateien repariert, {total_fixes} Fixes insgesamt!")


if __name__ == "__main__":
    fix_streamlit_deprecations()
