---
paths:
  - "**/docs/**"
description: "ドキュメント管理ルール（frontmatter・ステータス運用）"
---

## ドキュメント管理ルール

### 日付の記載

ファイル先頭に YAML frontmatter で作成日・最終更新日・ステータスを記載する。

- `WIP` — 作成中
- `ACCEPTED` — 完成
- `ARCHIVED` — 古くなったもの

AIは `WIP` と `ACCEPTED` のドキュメントを参照する。`ARCHIVED` は指示されない限り参照しない。

```markdown
---
作成日: 2025-11-19
最終更新: 2025-11-20
ステータス: WIP
---

# タイトル
```
