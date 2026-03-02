# kmBoxNet Python API Reference

> 本文件整理自官方 kmBoxNet Wiki 與 GitHub 範例  
> 適用模組：`kmNet.pyd`  
> 適用語言：Python  
> 主要用途：透過 kmBoxNet 裝置進行鍵盤 / 滑鼠控制與實體狀態監控

官方資源：
- 官方 Wiki（總覽）：https://www.kmbox.top/wiki_doc/kmboxNet/site/
- 官方 Wiki（Python）：https://www.kmbox.top/wiki_doc/kmboxNet/site/python/
- GitHub Repo：https://github.com/kvmaibox/kmboxnet

---

## 目錄

- [1. 環境與模組載入](#1-環境與模組載入)
- [2. 裝置初始化](#2-裝置初始化)
- [3. 滑鼠控制 API](#3-滑鼠控制-api)
  - [3.1 基礎位移](#31-基礎位移)
  - [3.2 滑鼠按鍵](#32-滑鼠按鍵)
  - [3.3 滾輪](#33-滾輪)
  - [3.4 綜合滑鼠控制](#34-綜合滑鼠控制)
  - [3.5 擬人化滑鼠移動](#35-擬人化滑鼠移動)
- [4. 鍵盤控制 API](#4-鍵盤控制-api)
- [5. 實體鍵鼠監控（Monitor）](#5-實體鍵鼠監控monitor)
- [6. API 快速索引](#6-api-快速索引)
- [7. 注意事項與實務建議](#7-注意事項與實務建議)

---

## 1. 環境與模組載入

### 模組放置位置
`kmNet.pyd` 必須放在 **對應 Python 版本** 的目錄中，例如：

- Windows：
```

PythonXX/DLLs/kmNet.pyd

````

### 載入方式
```python
import kmNet
````

---

## 2. 裝置初始化

### `init(ip: str, port: str, uuid: str) -> int`

**用途**
初始化 kmBoxNet 裝置連線（所有 API 使用前必須呼叫）

**參數**

| 參數   | 說明                |
| ---- | ----------------- |
| ip   | kmBoxNet 裝置 IP    |
| port | 通訊埠（例如 `6234`）    |
| uuid | 裝置 UUID（以盒子螢幕顯示為準） |

**回傳值**

| 值   | 說明         |
| --- | ---------- |
| 0   | 成功         |
| 非 0 | 初始化失敗（錯誤碼） |

**範例**

```python
ret = kmNet.init("192.168.2.88", "6234", "12345")
```

---

## 3. 滑鼠控制 API

> 所有 `enc_*` 函式皆為「**加密封包版本**」，功能等同原始版本
> 官方描述：加密封包較不易被流量特徵識別

---

### 3.1 基礎位移

#### `move(x: int, y: int) -> int`

立即移動滑鼠（無軌跡、最快）

```python
kmNet.move(50, -20)
```

#### `enc_move(x: int, y: int) -> int`

加密版本

---

### 3.2 滑鼠按鍵

| 函式               | 說明 |
| ---------------- | -- |
| `left(isdown)`   | 左鍵 |
| `right(isdown)`  | 右鍵 |
| `middle(isdown)` | 中鍵 |

* `isdown = 1`：按下
* `isdown = 0`：放開

```python
kmNet.left(1)
kmNet.left(0)
```

對應加密版本：

* `enc_left`
* `enc_right`
* `enc_middle`

---

### 3.3 滾輪

#### `wheel(delta: int) -> int`

| delta | 行為  |
| ----- | --- |
| > 0   | 向下滾 |
| < 0   | 向上滾 |

```python
kmNet.wheel(5)
```

加密版本：`enc_wheel(delta)`

---

### 3.4 綜合滑鼠控制

#### `mouse(btn: int, x: int, y: int, wheel: int) -> int`

一次設定 **按鍵 + 位移 + 滾輪**

**參數**

| 參數    | 範圍             |
| ----- | -------------- |
| btn   | 按鍵 bitmask     |
| x     | -32768 ~ 32768 |
| y     | -32768 ~ 32768 |
| wheel | -128 ~ 128     |

```python
kmNet.mouse(0, 10, 0, 0)
```

加密版本：`enc_mouse(...)`

---

### 3.5 擬人化滑鼠移動

#### `move_auto(x: int, y: int, ms: int) -> int`

* 以最小步進方式逼近目標
* `ms` 為期望耗時（實際通常略小）

```python
kmNet.move_auto(100, 50, 120)
```

加密版本：`enc_move_auto(...)`

---

#### `move_beizer(x, y, ms, x1, y1, x2, y2) -> int`

二階 Bezier 曲線移動（更自然）

```python
kmNet.move_beizer(100, 50, 150, 30, 10, 60, 20)
```

加密版本：`enc_move_beizer(...)`

---

## 4. 鍵盤控制 API

> `key` 為鍵盤鍵值（HID / Virtual Key，請參考官方附錄或 GitHub demo）

#### `keydown(key: int) -> int`

```python
kmNet.keydown(65)  # A
```

#### `keyup(key: int) -> int`

```python
kmNet.keyup(65)
```

加密版本：

* `enc_keydown`
* `enc_keyup`

---

## 5. 實體鍵鼠監控（Monitor）

### `monitor(port: int) -> int`

啟用或關閉「實體鍵鼠監控」

| port         | 行為   |
| ------------ | ---- |
| 1024 ~ 49151 | 啟用監控 |
| 0            | 關閉   |

```python
kmNet.monitor(30000)
```

---

### `isdown_left() -> int`

查詢實體滑鼠左鍵

| 回傳 | 狀態 |
| -- | -- |
| 0  | 未按 |
| 1  | 按下 |

```python
if kmNet.isdown_left():
    print("Left button pressed")
```

---

### `isdown_middle() -> int`

查詢實體滑鼠中鍵

---

## 6. API 快速索引

### 初始化

* `init`

### 滑鼠

* `move`, `enc_move`
* `left`, `right`, `middle`
* `wheel`
* `mouse`, `enc_mouse`
* `move_auto`, `move_beizer`

### 鍵盤

* `keydown`, `keyup`

### 監控

* `monitor`
* `isdown_left`
* `isdown_middle`

---

## 7. 注意事項與實務建議

* `init()` 必須成功後才能呼叫其他 API
* `move()` 與 `mouse()` 屬於**瞬移**，極不擬人
* `move_auto / move_beizer` 更適合長時間連續控制
* `enc_*` 建議作為正式部署版本使用
* Monitor 功能適合用於：

  * 人機混合控制
  * 物理鍵鼠狀態同步
  * 防止自動化誤觸
