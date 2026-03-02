# Ferrum Keyboard and Mouse API Reference

> 本文件整理自 Ferrum LLC 官方 KM API 文檔  
> 適用設備：Ferrum 鍵鼠控制設備  
> 主要用途：透過 Ferrum 裝置進行鍵盤 / 滑鼠控制與實體狀態監控

官方資源：
- 官方 API 文檔：https://ferrumllc.github.io/software_api/km_api.html

---

## 目錄

- [1. 系統概覽](#1-系統概覽)
- [2. 裝置初始化](#2-裝置初始化)
- [3. 滑鼠控制 API](#3-滑鼠控制-api)
  - [3.1 滑鼠按鍵](#31-滑鼠按鍵)
  - [3.2 滑鼠移動](#32-滑鼠移動)
  - [3.3 滾輪控制](#33-滾輪控制)
- [4. 鍵盤控制 API](#4-鍵盤控制-api)
  - [4.1 按鍵操作](#41-按鍵操作)
  - [4.2 按鍵屏蔽](#42-按鍵屏蔽)
- [5. 實體狀態監控](#5-實體狀態監控)
  - [5.1 讀取按鍵狀態](#51-讀取按鍵狀態)
  - [5.2 讀取滑鼠按鈕狀態](#52-讀取滑鼠按鈕狀態)
- [6. API 快速索引](#6-api-快速索引)
- [7. 注意事項與實務建議](#7-注意事項與實務建議)

---

## 1. 系統概覽

### 1.1 API 特性

Ferrum Keyboard and Mouse API (KM API) 是一套簡單的命令集，用於控制 Ferrum 設備的功能。主要功能包括：

- **按鍵控制**：按下和釋放滑鼠按鈕或鍵盤按鍵
- **按鍵屏蔽**：阻止按鍵發送到輸出電腦
- **狀態讀取**：讀取外設上實體按鈕或按鍵的狀態

### 1.2 通訊方式

Ferrum KM API 支援多種通訊方式，具體取決於設備型號：

- **USB HID**：直接 USB 連接
- **串口通訊**：透過 Serial Port 進行通訊
- **網路通訊**：透過網路協議進行遠端控制（部分型號）

---

## 2. 裝置初始化

### 2.1 連接設備

在使用 Ferrum KM API 之前，需要先連接並初始化設備。具體初始化方式取決於使用的通訊介面。

**USB HID 連接範例**：
```python
# 需要根據實際的 Python 綁定庫進行初始化
# 此處為偽代碼示例
import ferrum_km

device = ferrum_km.connect()
```

**串口連接範例**：
```python
import serial

ser = serial.Serial('COM3', 115200)  # 根據實際串口調整
```

**網路連接範例**：
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 8080))  # 根據實際 IP 和端口調整
```

---

## 3. 滑鼠控制 API

### 3.1 滑鼠按鍵

#### `mouse_button_press(button: int) -> bool`

按下指定的滑鼠按鈕。

**參數**

| 參數   | 說明                    | 值範圍        |
| ---- | --------------------- | ---------- |
| button | 滑鼠按鈕代碼                | 見按鈕代碼表    |

**按鈕代碼表**

| 代碼 | 按鈕   |
| -- | ---- |
| 1  | 左鍵   |
| 2  | 右鍵   |
| 4  | 中鍵   |
| 8  | 側鍵1  |
| 16 | 側鍵2  |

**回傳值**

| 值     | 說明   |
| ----- | ---- |
| True  | 成功   |
| False | 失敗   |

**範例**
```python
# 按下左鍵
ferrum_km.mouse_button_press(1)

# 按下右鍵
ferrum_km.mouse_button_press(2)
```

#### `mouse_button_release(button: int) -> bool`

釋放指定的滑鼠按鈕。

**參數**

| 參數   | 說明     | 值範圍     |
| ---- | ------ | ------- |
| button | 滑鼠按鈕代碼 | 見按鈕代碼表 |

**範例**
```python
# 釋放左鍵
ferrum_km.mouse_button_release(1)
```

#### `mouse_button_click(button: int, duration: int = 50) -> bool`

點擊指定的滑鼠按鈕（按下後立即釋放）。

**參數**

| 參數      | 說明        | 預設值 |
| ------- | --------- | --- |
| button  | 滑鼠按鈕代碼    | -   |
| duration | 按下持續時間（毫秒） | 50  |

**範例**
```python
# 單擊左鍵
ferrum_km.mouse_button_click(1)

# 單擊右鍵，持續 100 毫秒
ferrum_km.mouse_button_click(2, 100)
```

---

### 3.2 滑鼠移動

#### `mouse_move(x: int, y: int) -> bool`

相對移動滑鼠。

**參數**

| 參數 | 說明      | 範圍           |
| -- | ------- | ------------ |
| x  | X 軸相對位移 | -32768 ~ 32767 |
| y  | Y 軸相對位移 | -32768 ~ 32767 |

**範例**
```python
# 向右移動 100 像素，向下移動 50 像素
ferrum_km.mouse_move(100, 50)

# 向左移動 50 像素，向上移動 30 像素
ferrum_km.mouse_move(-50, -30)
```

#### `mouse_move_to(x: int, y: int) -> bool`

移動滑鼠到絕對座標（需要先設定螢幕解析度）。

**參數**

| 參數 | 說明      | 範圍 |
| -- | ------- | -- |
| x  | X 軸絕對座標 | 0+ |
| y  | Y 軸絕對座標 | 0+ |

**範例**
```python
# 移動到螢幕中心 (1920x1080)
ferrum_km.mouse_move_to(960, 540)
```

---

### 3.3 滾輪控制

#### `mouse_wheel(delta: int) -> bool`

滾動滑鼠滾輪。

**參數**

| 參數    | 說明      | 範圍        |
| ----- | ------- | --------- |
| delta | 滾輪滾動量   | -128 ~ 127 |
|       | 正值：向下滾動 |           |
|       | 負值：向上滾動 |           |

**範例**
```python
# 向下滾動
ferrum_km.mouse_wheel(3)

# 向上滾動
ferrum_km.mouse_wheel(-3)
```

---

## 4. 鍵盤控制 API

### 4.1 按鍵操作

#### `key_press(key: int) -> bool`

按下指定的鍵盤按鍵。

**參數**

| 參數  | 說明      | 格式        |
| --- | ------- | --------- |
| key | 鍵盤按鍵代碼 | HID Key Code |

**回傳值**

| 值     | 說明   |
| ----- | ---- |
| True  | 成功   |
| False | 失敗   |

**範例**
```python
# 按下 A 鍵 (HID Code: 0x04)
ferrum_km.key_press(0x04)

# 按下 Enter 鍵 (HID Code: 0x28)
ferrum_km.key_press(0x28)
```

#### `key_release(key: int) -> bool`

釋放指定的鍵盤按鍵。

**參數**

| 參數  | 說明      | 格式        |
| --- | ------- | --------- |
| key | 鍵盤按鍵代碼 | HID Key Code |

**範例**
```python
# 釋放 A 鍵
ferrum_km.key_release(0x04)
```

#### `key_click(key: int, duration: int = 50) -> bool`

點擊指定的鍵盤按鍵（按下後立即釋放）。

**參數**

| 參數      | 說明        | 預設值 |
| ------- | --------- | --- |
| key     | 鍵盤按鍵代碼    | -   |
| duration | 按下持續時間（毫秒） | 50  |

**範例**
```python
# 單擊 A 鍵
ferrum_km.key_click(0x04)

# 單擊 Enter 鍵，持續 100 毫秒
ferrum_km.key_click(0x28, 100)
```

#### `key_combination(keys: list) -> bool`

按下多個按鍵組合（例如 Ctrl+C）。

**參數**

| 參數   | 說明        | 格式           |
| ---- | --------- | ------------ |
| keys | 按鍵代碼列表    | HID Key Code 列表 |

**範例**
```python
# Ctrl+C (Ctrl: 0xE0, C: 0x06)
ferrum_km.key_combination([0xE0, 0x06])

# Alt+Tab (Alt: 0xE2, Tab: 0x2B)
ferrum_km.key_combination([0xE2, 0x2B])
```

---

### 4.2 按鍵屏蔽

#### `key_block(key: int, enable: bool) -> bool`

阻止指定的按鍵發送到輸出電腦。

**參數**

| 參數     | 說明     | 格式        |
| ------ | ------ | --------- |
| key    | 鍵盤按鍵代碼 | HID Key Code |
| enable | 是否啟用屏蔽 | True/False |

**回傳值**

| 值     | 說明   |
| ----- | ---- |
| True  | 成功   |
| False | 失敗   |

**範例**
```python
# 屏蔽 A 鍵（按下 A 鍵不會發送到電腦）
ferrum_km.key_block(0x04, True)

# 解除屏蔽 A 鍵
ferrum_km.key_block(0x04, False)
```

#### `mouse_button_block(button: int, enable: bool) -> bool`

阻止指定的滑鼠按鈕發送到輸出電腦。

**參數**

| 參數     | 說明     | 格式        |
| ------ | ------ | --------- |
| button | 滑鼠按鈕代碼 | 見按鈕代碼表   |
| enable | 是否啟用屏蔽 | True/False |

**範例**
```python
# 屏蔽左鍵（按下左鍵不會發送到電腦）
ferrum_km.mouse_button_block(1, True)

# 解除屏蔽左鍵
ferrum_km.mouse_button_block(1, False)
```

---

## 5. 實體狀態監控

### 5.1 讀取按鍵狀態

#### `key_is_pressed(key: int) -> bool`

讀取指定鍵盤按鍵的實體狀態。

**參數**

| 參數  | 說明      | 格式        |
| --- | ------- | --------- |
| key | 鍵盤按鍵代碼 | HID Key Code |

**回傳值**

| 值     | 說明   |
| ----- | ---- |
| True  | 按下   |
| False | 未按下  |

**範例**
```python
# 檢查 A 鍵是否被按下
if ferrum_km.key_is_pressed(0x04):
    print("A key is pressed")
```

---

### 5.2 讀取滑鼠按鈕狀態

#### `mouse_button_is_pressed(button: int) -> bool`

讀取指定滑鼠按鈕的實體狀態。

**參數**

| 參數   | 說明     | 格式      |
| ---- | ------ | ------- |
| button | 滑鼠按鈕代碼 | 見按鈕代碼表 |

**回傳值**

| 值     | 說明   |
| ----- | ---- |
| True  | 按下   |
| False | 未按下  |

**範例**
```python
# 檢查左鍵是否被按下
if ferrum_km.mouse_button_is_pressed(1):
    print("Left button is pressed")

# 檢查右鍵是否被按下
if ferrum_km.mouse_button_is_pressed(2):
    print("Right button is pressed")
```

---

## 6. API 快速索引

### 滑鼠控制

| 功能     | API                        |
| ------ | -------------------------- |
| 按下按鈕   | `mouse_button_press`        |
| 釋放按鈕   | `mouse_button_release`      |
| 點擊按鈕   | `mouse_button_click`        |
| 相對移動   | `mouse_move`                |
| 絕對移動   | `mouse_move_to`             |
| 滾輪滾動   | `mouse_wheel`               |
| 讀取按鈕狀態 | `mouse_button_is_pressed`   |
| 屏蔽按鈕   | `mouse_button_block`        |

### 鍵盤控制

| 功能     | API                  |
| ------ | -------------------- |
| 按下按鍵   | `key_press`           |
| 釋放按鍵   | `key_release`         |
| 點擊按鍵   | `key_click`           |
| 按鍵組合   | `key_combination`     |
| 讀取按鍵狀態 | `key_is_pressed`      |
| 屏蔽按鍵   | `key_block`           |

---

## 7. 注意事項與實務建議

### 7.1 初始化與連接

- 使用 API 前必須先成功連接並初始化設備
- 不同型號的 Ferrum 設備可能使用不同的通訊方式（USB HID、串口、網路）
- 確保設備驅動程式已正確安裝

### 7.2 按鍵代碼

- 鍵盤按鍵使用 **HID Key Code** 標準
- 滑鼠按鈕使用位元掩碼（1=左鍵, 2=右鍵, 4=中鍵, 8=側鍵1, 16=側鍵2）
- 多個按鈕可同時按下（使用位元 OR 運算，例如：`1 | 2` 表示同時按下左鍵和右鍵）

### 7.3 按鍵屏蔽功能

- 屏蔽功能用於阻止實體按鍵輸入發送到輸出電腦
- 適用於需要完全控制輸入的場景
- 注意：屏蔽後，實體按鍵將無法正常使用，需手動解除屏蔽

### 7.4 狀態讀取

- 狀態讀取功能用於監控實體外設的狀態
- 可用於實現人機混合控制
- 讀取的是實體按鍵狀態，而非軟體模擬的按鍵狀態

### 7.5 效能考量

- 滑鼠移動和按鍵操作應避免過於頻繁，以免造成系統負擔
- 建議在操作之間加入適當的延遲
- 對於需要高頻操作的場景，考慮使用批量操作或流式介面（如果設備支援）

### 7.6 錯誤處理

- 所有 API 函式都應檢查回傳值
- 初始化失敗時，後續所有操作都可能失敗
- 建議實作重試機制和錯誤日誌記錄

### 7.7 相容性

- 不同版本的 Ferrum 設備可能支援不同的 API 功能
- 建議在實作前查閱設備特定的文檔
- 某些進階功能可能僅在特定型號上可用

---

## 附錄：常用 HID Key Codes

| 按鍵     | HID Code | 說明   |
| ------ | -------- | ---- |
| A-Z    | 0x04-0x1D | 字母鍵  |
| 0-9    | 0x1E-0x27 | 數字鍵  |
| Enter  | 0x28     | 回車鍵  |
| Esc    | 0x29     | 退出鍵  |
| Backspace | 0x2A  | 退格鍵  |
| Tab    | 0x2B     | 製表鍵  |
| Space  | 0x2C     | 空格鍵  |
| Ctrl   | 0xE0     | 左 Ctrl |
| Shift  | 0xE1     | 左 Shift |
| Alt    | 0xE2     | 左 Alt  |
| Win    | 0xE3     | 左 Win  |
| Ctrl-R | 0xE4     | 右 Ctrl |
| Shift-R | 0xE5    | 右 Shift |
| Alt-R  | 0xE6     | 右 Alt  |
| Win-R  | 0xE7     | 右 Win  |

> **注意**：完整的 HID Key Code 列表請參考官方文檔或 HID 標準規範。

---

**最後更新**：2025-01-20  
**文檔版本**：1.0.0  
**參考來源**：https://ferrumllc.github.io/software_api/km_api.html
