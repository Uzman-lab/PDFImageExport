# -*- coding: utf-8 -*-
import re

with open("pdf_to_images.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find _set_status calls with Turkish text not wrapped in _t()
# Pattern: _set_status("Turkish text") or _set_status(f"Turkish text")
lines = content.split("\n")
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    # Check if it starts with self._set_status or self.status.config
    if ("_set_status(" in stripped or "self.status.config(" in stripped) and \
       ("_t(" not in stripped):
        print(f"Line {i}: {stripped[:120]}")

print("---")
# Also check messagebox calls without _t
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if "messagebox." in stripped and "show" in stripped and "_t(" not in stripped:
        print(f"Line {i}: {stripped[:120]}")
