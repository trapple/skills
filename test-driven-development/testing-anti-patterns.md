# Testing Anti-Patterns

**読むべきとき:** テストを書く / 変える / mock を足す / production class に「テスト用 method」を生やしたくなったとき。

## 概要

テストは **real な振る舞い** を verify する。mock は isolate のための手段であり、test 対象そのものではない。

**Core principle:** code が何をするかをテストする、**mock が何をするかではない**。

TDD を厳守すればこれらの anti-pattern は構造的に発生しない。

## The Iron Laws

```
1. mock の振る舞いを test しない
2. production class に「test 専用 method」を生やさない
3. 依存を理解せずに mock しない
4. spec 違反を検出できないテストを書かない (冗長テスト禁止)
```

## Anti-Pattern 1: mock の振る舞いをテストしている

**違反:**

```javascript
// ❌ BAD: mock の存在をテストしている
test('renders sidebar', () => {
  render(Page());
  assert.ok(screen.getByTestId('sidebar-mock'));
});
```

**なぜ wrong か:**
- 「mock が存在する」ことを verify しているだけで、component の振る舞いをテストしていない
- mock があれば pass、無ければ fail。real な振る舞いについて何も語らない

**fix:**

```javascript
// ✅ GOOD: real な component をテストする (mock しない)
test('renders sidebar', () => {
  render(Page());
  assert.ok(screen.getByRole('navigation'));
});

// あるいは isolation のために mock が要るなら、
// mock そのものを assert しない。sidebar が存在することを前提として
// Page の振る舞いをテストする。
```

### ゲート

```
mock element に対して assert する前に:
  問う: 「私は real な component の振る舞いをテストしている? それとも mock の存在?」

  mock の存在をテストしているなら:
    止まる — その assertion を delete するか component を unmock する

  real な振る舞いをテストする
```

## Anti-Pattern 2: production class に「test 専用 method」

**違反:**

```javascript
// ❌ BAD: destroy() は test でしか使わない
class Session {
  async destroy() {  // production API のように見える
    await this._workspaceManager?.destroyWorkspace(this.id);
  }
}

// test 側
afterEach(() => session.destroy());
```

**なぜ wrong か:**
- production class が test のためのコードで汚れる
- 誤って production で呼ばれると危険
- YAGNI と関心の分離に違反
- object lifecycle と entity lifecycle の混同

**fix:**

```javascript
// ✅ GOOD: test utility が test cleanup を持つ
// Session は destroy() を持たない (production では stateless)

// test-utils/cleanup.mjs
export async function cleanupSession(session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// test 側
afterEach(() => cleanupSession(session));
```

### ゲート

```
production class に method を足す前に:
  問う: 「これは test でしか使わないか?」
  Yes → 足さない。test utility に置く

  問う: 「この class は本当にこのリソースの lifecycle を所有しているか?」
  No → 違う class。method の置き場所を間違えている
```

## Anti-Pattern 3: 依存を理解せず mock する

**違反:**

```javascript
// ❌ BAD: mock が test logic を壊している
test('detects duplicate server', () => {
  // mock が test に必要な「config 書き込み」side effect を消してしまう
  mock.method(ToolCatalog, 'discoverAndCacheTools', async () => undefined);

  await addServer(config);
  await addServer(config);  // throw されるべきだが mock が阻む
});
```

**なぜ wrong か:**
- mock した method の side effect (config 書き込み) に test が依存していた
- 「念のため」の過剰 mock が actual behavior を壊す
- test が間違った理由で pass、または mysterious に fail する

**fix:**

```javascript
// ✅ GOOD: 正しい level で mock する
test('detects duplicate server', () => {
  // 遅い部分 (MCPServerManager の起動) だけ mock。config 書き込みは本物
  mock.module('MCPServerManager');

  await addServer(config);  // config 書き込み実行
  await addServer(config);  // 重複検知 ✓
});
```

### ゲート

```
method を mock する前に:
  止まる。まだ mock しない

  1. 問う: 「この method は実際にどんな side effect を持つ?」
  2. 問う: 「test はそのうちのどれに依存している?」
  3. 問う: 「test が何を必要としているか完全に理解できているか?」

  side effect に依存しているなら:
    1 階層下で mock する (actual な slow/external 操作だけ)
    あるいは test double で必要な振る舞いを保つ
    test が依存している high-level method を mock しない

  test が何に依存しているか分からないなら:
    まず real 実装で test を走らせる
    何が起きる必要があるか観察する
    最小の mock を正しい level に追加する

  red flag:
    - 「念のため mock する」
    - 「遅そうだから mock する」
    - 依存の連鎖を理解せず mock する
```

## Anti-Pattern 4: 不完全な mock

**違反:**

```javascript
// ❌ BAD: 必要だと思ったフィールドだけ持つ partial mock
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // metadata 抜け — downstream code が response.metadata.requestId にアクセスして爆発
};
```

**なぜ wrong か:**
- **partial mock は構造的仮定を隠す** — 自分が知っているフィールドしか mock していない
- **downstream code が含めていないフィールドに依存している可能性** — silent failure
- **test pass / integration fail** — mock 不完全、real API 完全
- **誤った安心感** — real な振る舞いについて何も証明しない

**Iron Rule:** mock するなら、**real な data 構造の完全形** を mock する。直近の test が使うフィールドだけではない。

**fix:**

```javascript
// ✅ GOOD: real な API を完全にミラー
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // real API が返すフィールドを全部含める
};
```

### ゲート

```
mock レスポンスを作る前に:
  確認: 「real な API レスポンスのフィールドは何か?」

  手順:
    1. 実際の API レスポンスを doc / 実例で確認
    2. system が downstream で消費する可能性のあるフィールドを全部含める
    3. mock が real なレスポンス schema と完全に一致しているか verify

  critical:
    mock を作るなら、構造を 100% 理解している必要がある
    partial mock は含めていないフィールドに依存する code で silent fail する

  不確かなら、documented フィールドを全部入れる
```

## Anti-Pattern 5: integration test を後付けにする

**違反:**

```
✅ 実装完了
❌ test は書いていない
「test 待ち」
```

**なぜ wrong か:**
- test は実装の一部であり、optional な follow-up ではない
- TDD ならこれは構造的に発生しない
- test なしで「完了」を主張できない

**fix:**

```
TDD cycle:
1. 失敗する test を書く
2. pass するように実装
3. refactor
4. 「完了」を主張する
```

## Anti-Pattern 6: 過剰テスト / 冗長テスト

**違反:**

```javascript
// ❌ BAD: 同一 equivalence class の水増し — 同じ production code で扱われる入力を並べても検出力は増えない
test('rejects spaces-only email', ...);
test('rejects tab-only email', ...);      // trim に対して spaces と同一 class
test('rejects newline-only email', ...);  // 同上
test('rejects null email', ...);
test('rejects undefined email', ...);     // nullish は 1 class → どちらか 1 本

// ❌ BAD: 実装詳細を assert — 振る舞い不変の refactor で壊れる
test('calls validateEmail exactly once', () => {
  const spy = mock.method(validator, 'validateEmail');
  submitForm({ email: 'a@b.c' });
  assert.equal(spy.mock.callCount(), 1);
});
```

**なぜ wrong か:**
- 冗長テストは regression 検出力を上げず、保守コストとノイズだけ増やす
- 実装詳細テストは正しい refactor で fail し、「テストを通すために設計を歪める」逆転が起きる
- テストの本数が「よくテストされている」という誤った安心感を生む
- KISS 違反 — テストも保守対象のコード

**fix:**

```javascript
// ✅ GOOD: 要求される production code ごとに代表 1 点
test('rejects empty email', ...);           // === '' を強制 (境界)
test('rejects whitespace-only email', ...); // trim() を強制 (' \t\n ' で全字種を 1 本に)
test('rejects missing email', ...);         // ?. を強制 (nullish の代表)
```

### ゲート

```
テストを 1 本足す前に (SKILL.md「必要十分」のゲートと同一規則):
  問う: 「この入力を正しく扱うために、既存テストが強制していない
         production code の追加・変更が必要か?」
    Yes → 別 class。書く
    No  → 同一 class。書かない
         (例外は spec が明示する境界ちょうどの値を代表に選ぶことのみ。
          mutation を捏造して「この点だけ fail する改変がある」と
          正当化するのは過剰テスト)

  注意: spec にある振る舞い・境界・エラー経路を「過剰」と呼んで
  省くのは逆方向の違反。必要十分 = spec の全振る舞いを 1 回ずつ
```

## mock が複雑になりすぎたとき

**warning sign:**
- mock setup が test logic より長い
- pass させるために何でも mock している
- mock が real component に存在する method を欠いている
- mock を変えると test が壊れる

**問い直し:** 「ここで mock を使う必要が本当にあるか?」

**検討:** real component を使う integration test の方が複雑な mock より simple なことが多い

## TDD が anti-pattern を構造的に防ぐ理由

1. **test 先行** → 「何をテストしているのか」を実装前に考える必要がある
2. **失敗を見る** → mock ではなく real な振る舞いをテストしていることが確認される
3. **最小実装** → test 用 method が production に crept in する余地が無くなる
4. **real な依存** → mock する前に test が何を必要としているか見える

**mock の振る舞いを test しているなら、TDD が破られている** — real なコードに対して test が fail することを確認せずに mock を足した結果。

## Quick Reference

| anti-pattern | fix |
|---|---|
| mock element に assert | real component を test、または unmock |
| production に test 専用 method | test utility に移す |
| 依存を理解せず mock | 依存を先に理解、最小限で mock |
| 不完全な mock | real API を完全ミラー |
| test を後付け | TDD — test 先行 |
| 過剰 mock | integration test を検討 |
| 過剰 / 冗長テスト | equivalence class 代表 + 境界に絞る |

## Red Flag

- assertion が `*-mock` test ID を check している
- test ファイルでしか呼ばれない method が production にある
- mock setup が test の 50% 超
- mock を外すと test が fail する
- mock を入れている理由が説明できない
- 「念のため」mock している
- 振る舞い不変の refactor でテストが壊れる
- 複数のテストが同じ分岐を通っている
- テスト内に if / try-catch での成否分岐がある

## Bottom Line

**mock は isolate のための tool であり、test 対象ではない。**

TDD が「mock の振る舞いをテストしている」と告げてきたら、どこかで道を間違えた。

fix: real な振る舞いをテストする、もしくは「なぜ mock しているのか」を問い直す。

## 副作用の DI 化 — 汎用パターン

外部 API / DB / fs などの副作用は **引数注入** で stub 可能な構造を維持する。PJ で確立した DI パターンがあればそれに合わせる。一般形:

```javascript
// production
export async function pushFiles(srcDir, { client, fs } = { client: defaultClient, fs: defaultFs }) {
  // ...
}

// test (anti-pattern 4 を避けるため stub は real な client interface を全部持つ)
test('pushFiles uploads new files only', async () => {
  const clientStub = {
    list: async () => [{ name: 'a.bin', checksum: 'aaa' }],
    upload: async (...) => { /* ... */ },
    findFolder: async () => ({ id: 'folder-id' }),
    // real interface を完全にミラー
  };
  const result = await pushFiles('/path', { client: clientStub, fs: realFs });
  // ...
});
```

**Fail Fast 原則と合わせる:** stub の error 経路もテストする。stub が throw したときに **production code が silent skip せず throw 伝播する** ことを test で verify する。PJ CLAUDE.md / `.claude/rules/error-handling.md` 等に Fail Fast 規約があれば、それと整合させる。
