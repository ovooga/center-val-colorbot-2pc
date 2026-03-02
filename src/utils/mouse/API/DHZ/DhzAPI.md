# DHZ API Reference（Ethernet / UDP）
## 1. 系統概覽

### 1.1 通訊模型

* **協議**：UDP
* **資料格式**：ASCII 指令字串（Caesar 位移加密）
* **方向**：

  * Host → Device：控制命令
  * Device → Host：狀態回傳（monitor 模式）

### 1.2 初始化參數

```python
DHZBOX(IP, PORT, RANDOM)
```

| 參數     | 說明         |
| ------ | ---------- |
| IP     | 設備 IP 位址   |
| PORT   | 控制端口（UDP）  |
| RANDOM | 加密位移金鑰（整數） |

---

## 2. 指令加密機制

* 所有指令在送出前會經過 **Caesar Cipher 位移加密**
* 僅對英文字母進行位移，其餘字元不變

```text
move(10,5)  →  加密後字串
```

> RANDOM 即為位移量（0–25）。

---

## 3. 滑鼠控制 API

### 3.1 移動

```python
move(x, y)
```

* 功能：相對移動滑鼠
* 參數：

  * x：X 軸位移
  * y：Y 軸位移

---

### 3.2 按鍵控制

| 功能  | API             | state 說明  |
| --- | --------------- | --------- |
| 左鍵  | `left(state)`   | 1=按下，0=釋放 |
| 右鍵  | `right(state)`  | 1=按下，0=釋放 |
| 中鍵  | `middle(state)` | 1=按下，0=釋放 |
| 側鍵1 | `side1(state)`  | 1=按下，0=釋放 |
| 側鍵2 | `side2(state)`  | 1=按下，0=釋放 |

---

### 3.3 滾輪

```python
wheel(delta)
```

* delta：滾輪方向與幅度（正 / 負）

---

### 3.4 組合滑鼠幀

```python
mouse(button, x, y, wheel)
```

| 參數     | 說明   |
| ------ | ---- |
| button | 按鍵掩碼 |
| x,y    | 移動量  |
| wheel  | 滾輪值  |

---

## 4. 鍵盤控制 API

### 4.1 按鍵操作

```python
keydown(key)
keyup(key)
```

* key：字串形式鍵名（如 `KEY_A`）

---

## 5. 狀態監聽（Monitor）

### 5.1 啟用 / 停用

```python
monitor(port)
```

| port | 行為               |
| ---- | ---------------- |
| 0    | 關閉監聽             |
| >0   | 啟用監聽並綁定 UDP port |

設備會主動回傳狀態資料。

---

### 5.2 狀態查詢 API

| 功能   | API               |
| ---- | ----------------- |
| 左鍵狀態 | `isdown_left()`   |
| 中鍵狀態 | `isdown_middle()` |
| 右鍵狀態 | `isdown_right()`  |
| 側鍵1  | `isdown_side1()`  |
| 側鍵2  | `isdown_side2()`  |
| 所有鍵  | `isdown()`        |
| 指定鍵  | `isdown2(key)`    |

---

## 6. 屏蔽 / 掩碼（Mask）API

### 6.1 滑鼠屏蔽

| 功能  | API                  |
| --- | -------------------- |
| 左鍵  | `mask_left(state)`   |
| 右鍵  | `mask_right(state)`  |
| 中鍵  | `mask_middle(state)` |
| 滾輪  | `mask_wheel(state)`  |
| X 軸 | `mask_x(state)`      |
| Y 軸 | `mask_y(state)`      |
| 側鍵1 | `mask_side1(state)`  |
| 側鍵2 | `mask_side2(state)`  |
| 全部  | `mask_all(state)`    |

state：1=屏蔽，0=解除

---

### 6.2 鍵盤屏蔽

```python
mask_keyboard(key)
dismask_keyboard(key)
dismask_keyboard_all()
```

---

## 7. 指令傳輸特性

* 每次指令：

  * UDP 單包傳輸
  * 等待回碼（0.1s timeout）
  * 超時會自動重發

---

## 8. 設計定位與比較

| 項目    | DHZ API    | makxd V2       |
| ----- | ---------- | -------------- |
| 傳輸    | UDP        | UART / USB     |
| 指令    | ASCII + 加密 | ASCII / Binary |
| 即時性   | 高（LAN）     | 極高（本地）         |
| SDK 層 | Python 為主  | 多語言            |