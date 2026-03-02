## 📄 Arduino API 文件（arduino.md）

````markdown
# Arduino Serial Control API（SunOner_Aimbot_CPP）

此文檔整理自  
📌 `Arduino.h`  
📌 `Arduino.cpp`  
來源: https://github.com/SunOner/sunone_aimbot_cpp

---

## 1. 類別說明

類別：`Arduino`

用途：透過 **Serial（UART / COM Port）** 控制 Arduino 端的滑鼠與狀態回報。

---

## 2. 建構與解構

### 建構函式

```cpp
Arduino(const std::string& port, unsigned int baud_rate);
````

* `port`：連接的串口設備（如 `"COM3"`）
* `baud_rate`：波特率（如 9600 / 115200）

例：

```cpp
Arduino arduino("COM3", 115200);
```

---

### 解構函式

```cpp
~Arduino();
```

* 自動關閉串口
* 終止監聽執行緒

---

## 3. 核心狀態查詢

```cpp
bool isOpen() const;
```

* 回傳 Arduino 是否成功開啟 Serial Port

---

## 4. 底層讀寫

### 寫入字串

```cpp
void write(const std::string& data);
```

* 透過串口發送命令

### 讀取一行

```cpp
std::string read();
```

* 從 Serial 讀取到換行（`\n`）為止

---

## 5. 滑鼠控制方法

---

### 5.1 單擊

```cpp
void click();
```

底層會 sendCommand `"c"`：

```cpp
c\n
```

---

### 5.2 按下（半按）

```cpp
void press();
```

底層會 sendCommand `"p"`：

```cpp
p\n
```

---

### 5.3 釋放

```cpp
void release();
```

底層會 sendCommand `"r"`：

```cpp
r\n
```

---

### 5.4 滑鼠移動

```cpp
void move(int x, int y);
```

| 參數 | 說明     |
| -- | ------ |
| x  | X 軸移動量 |
| y  | Y 軸移動量 |

---

#### 5.4.1 16-bit 直發模式

若 `config.arduino_16_bit_mouse == true`

```cpp
std::string data = "m" + std::to_string(x) + "," + std::to_string(y) + "\n";
write(data);
```

等同串口發：

```
m10,5\n
```

---

#### 5.4.2 分段模式（拆成 -127..127）

若超過 127，會拆成多個部分送出

舉例：

```
m250,30 → m127,30 + m123,0
```

---

## 6. 底層指令封裝

```cpp
void sendCommand(const std::string& command);
```

等同：

```
command + "\n"
```

---

## 7. 非同步機制與監聽

為了接收 Arduino 端回報的按鍵／狀態變化，Internal 有：

* `std::thread timer_thread_`
* `std::thread listening_thread_`
* `listeningThreadFunc()`
* `processIncomingLine(line)`

---

### 7.1 Listening Thread

會不斷讀串口資料：

```cpp
serial_.available();
serial_.read();
```

遇到 `'\n'` 為一完整行，交給：

```cpp
processIncomingLine(line);
```

---

## 8. 回報解析邏輯

Arduino 端回報格式：

```
BD:<buttonId>
BU:<buttonId>
```

---

### 8.1 處理 `BD:`（Button Down）

```cpp
if (line.rfind("BD:", 0) == 0) { ... }
```

| buttonId | 對應狀態                   |
| -------- | ---------------------- |
| 2        | aiming_active = true   |
| 1        | shooting_active = true |

---

### 8.2 處理 `BU:`（Button Up）

```cpp
if (line.rfind("BU:", 0) == 0) { ... }
```

對應設定 active 狀態為 `false`

---

## 9. 內部輔助函式

### splitValue

拆分大於 127 的移動量成可分包部分

---

## 10. 成員變數（Key Flags）

| 變數              | 類型           | 說明          |
| --------------- | ------------ | ----------- |
| aiming_active   | bool         | 是否正在輔助瞄準    |
| shooting_active | bool         | 是否正在射擊      |
| zooming_active  | bool         | 是否正在放大      |
| is_open_        | atomic<bool> | Serial 是否開啟 |
| listening_      | atomic<bool> | 監聽是否啟動      |

---

## 11. 使用示例

```cpp
Arduino arduino("COM4", 115200);

if (arduino.isOpen()) {
    arduino.click();
    arduino.move(10, -5);
}
```

---

## 12. 協議總結（ARDUINO 端）

| 字元     | 意義           |
| ------ | ------------ |
| `c`    | click        |
| `p`    | press        |
| `r`    | release      |
| `mX,Y` | move by X, Y |
| `\n`   | 終止符號         |
