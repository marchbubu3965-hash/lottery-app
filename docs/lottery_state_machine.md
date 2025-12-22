IDLE
 └─ start() ─▶ RUNNING
RUNNING
 └─ finish_round() ─▶ WAIT_NEXT
WAIT_NEXT
 └─ next_round() ─▶ RUNNING

 # Lottery State Machine

## 狀態列表

| 狀態 | 說明 |
|------|------|
| IDLE | 系統就緒，尚未開始抽獎 |
| RUNNING | 抽獎中 |
| PAUSED | 暫停抽獎 |
| WAIT_NEXT | 本輪抽獎結束，等待下一個獎項 |
| FINISHED | 所有獎項抽完，抽獎完成 |

## 方法說明

### `start()`
- 條件：`IDLE`
- 動作：開始抽獎 → 狀態變 `RUNNING`
- 例外：非 IDLE 狀態呼叫會拋出 `InvalidStateTransition`

### `pause()`
- 條件：`RUNNING`
- 動作：暫停抽獎 → 狀態變 `PAUSED`

### `resume()`
- 條件：`PAUSED`
- 動作：繼續抽獎 → 狀態變 `RUNNING`

### `wait_next()`
- 條件：`RUNNING`
- 動作：本輪抽獎結束 → 狀態變 `WAIT_NEXT`

### `next_round()`
- 條件：`WAIT_NEXT`
- 動作：開始下一個獎項抽獎 → 狀態變 `RUNNING`

### `finish()`
- 條件：`RUNNING` 或 `WAIT_NEXT`
- 動作：抽獎結束 → 狀態變 `FINISHED`

### `reset()`
- 動作：重置狀態 → 狀態變 `IDLE`

## 錯誤處理
- 所有非法狀態轉換會拋出 `InvalidStateTransition`，防止流程錯亂。

---

> 提示：本文件可作為程式設計與單元測試的參考，確保抽獎流程符合預期。

