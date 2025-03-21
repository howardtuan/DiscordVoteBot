# Discord 遊戲投票機器人

這是一個簡單的 Discord 機器人，專門用於創建遊戲投票。機器人可以每天晚上 7:30 自動發送投票，詢問成員們是否要進行遊戲，並提供「要」和「不要」兩個選項供成員選擇。投票結果會顯示所有參與投票的成員名稱。

## 功能特色

- 每天晚上 7:30 自動發送投票
- 可使用指令手動觸發投票
- 實時顯示投票結果和參與者名稱
- 使用成員在伺服器中的暱稱
- 投票自動在 1 小時後結束
- 可手動取消正在進行的投票

## 檔案結構

```
discord-game-poll-bot/
├── .env.example           # 環境變數範例檔案
├── bot.py                 # 機器人主程式
├── requirements.txt       # 相依套件清單
└── README.md              # 專案說明文件
```

## 安裝指南

### 前置需求

- Python 3.8 或更高版本
- Discord Bot Token（從 [Discord 開發者平台](https://discord.com/developers/applications) 取得）

### 步驟 1: 複製專案

```bash
git clone https://github.com/yourusername/discord-game-poll-bot.git
cd discord-game-poll-bot
```

### 步驟 2: 設置虛擬環境

```bash
# 建立虛擬環境
python -m venv venv

# 在 Windows 上啟用虛擬環境
venv\Scripts\activate

# 在 macOS/Linux 上啟用虛擬環境
source venv/bin/activate
```

### 步驟 3: 安裝相依套件

```bash
pip install -r requirements.txt
```

### 步驟 4: 設定環境變數

將 `.env.example` 複製為 `.env` 並填入你的機器人 Token 和目標頻道 ID：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```
BOT_TOKEN=你的機器人Token
CHANNEL_ID=你想發送自動投票的頻道ID
```

### 步驟 5: 在 Discord 開發者平台啟用必要權限

1. 前往 [Discord 開發者平台](https://discord.com/developers/applications)
2. 選擇你的機器人應用程式
3. 點擊「Bot」選項卡
4. 在「Privileged Gateway Intents」下啟用以下權限：
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
5. 儲存變更

## 使用說明

### 啟動機器人

```bash
# 確認已啟用虛擬環境
python bot.py
```

### 可用指令

- `!poll` - 在當前頻道立即發送投票
- `!cancelpoll` - 取消當前頻道中正在進行的投票

### 自動功能

機器人會在每天晚上 7:30 自動在設定的頻道中發送投票，投票將在 1 小時後自動結束。

## 自訂設定

如果你想更改投票時間或其他設定，可以編輯 `bot.py` 中的相關參數：

- 修改投票持續時間：調整 `await asyncio.sleep(3600)` 中的數值（以秒為單位）
- 修改自動發送時間：調整 `@tasks.loop(time=datetime.time(hour=19, minute=30))` 中的時間

## 授權條款

MIT 授權
