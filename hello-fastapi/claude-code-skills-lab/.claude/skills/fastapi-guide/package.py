#!/usr/bin/env python3
"""Package the skill into a .skill file."""

import zipfile
from pathlib import Path

def package_skill():
    skill_dir = Path(__file__).parent
    output_file = skill_dir.parent.parent.parent / "fastapi-guide.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file() and file_path.name != 'package.py':
                arcname = file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nSkill packaged successfully: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    package_skill()
