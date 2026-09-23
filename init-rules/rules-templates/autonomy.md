---
paths:
  - "**/*"
description: "自律モード宣言（autonomous / guarded の既定と、慎重に扱う領域）"
---

## 自律モード宣言

brainstorming → writing-plans → subagent-driven-development のパイプラインを、どこまで人間の確認なしで進めてよいかを宣言する。判定ロジックとゲートの中身は `cross-review` スキルにある。このファイルはユーザーの明示発話の次に優先される。

### 既定モード

```yaml
default: auto   # auto (Auto Mode 有効なら autonomous、それ以外は guarded) / autonomous / guarded
```

### 常に guarded にする領域

以下に触れる spec / タスクは、モードに関係なく人間の確認を挟む (該当タスクに `**Gate: human**` を付ける。案件全体が該当するなら guarded で進める)。PJ に合わせて追加・削除する。

- `migrations/**` — DB スキーマ変更
- `**/billing/**`, `**/payment/**` — 課金
- `**/auth/**` — 認証 / 認可
- `infra/**`, `deploy/**`, `.github/workflows/**` — デプロイ / CI
- 本番データを読み書きするスクリプト

### autonomous でも止まる操作

cross-review スキルの「必ず止まる条件」に加えて、この PJ で止めたいものを書く (例: 外部 SaaS の API キーを使う処理、公開ドキュメントの更新)。

- （なし）
