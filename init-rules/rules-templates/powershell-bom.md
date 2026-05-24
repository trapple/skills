---
paths:
  - "**/*.ps1"
description: "PowerShell ファイルは BOM 付き UTF-8 で保存"
---

## PowerShell ファイルのエンコーディング

`.ps1` ファイルは BOM 付き UTF-8（UTF-8 with BOM）で保存すること。
BOM がないと日本語が文字化けする。
