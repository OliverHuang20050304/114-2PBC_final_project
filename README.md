# GLOBAL STAR：成名之路

以 Python 與 **CustomTkinter** 製作的 GUI 敘事模擬遊戲。玩家扮演剛與 **Creative Artist Records** 簽約的新人歌手，從選擇落腳城市、出道風格開始，在名氣、形象、健康、金錢、自我認同與爭議度之間做出取捨，走向不同的第二章路線，並在第三章依累積數值解鎖多種結局。

---

## 安裝與執行

### 安裝依賴

建議使用虛擬環境：

```bash
python -m venv env
source env/bin/activate   # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 執行遊戲

```bash
python main.py
```

---

## 遊戲介紹

### 故事背景

你是一位來自普通家庭的新人，剛簽約大型經紀公司。出道曲、首張專輯、巡演、公關危機、病毒式爆紅……每一個選擇都會改變你在產業中的位置，也會改變你與「真實的自己」之間的距離。

### 遊戲流程概覽

| 章節 | 內容 |
|------|------|
| **序章** | 選擇發展城市（洛杉磯 / 倫敦 / 紐約）、出道風格（叛逆 / 商業流行 / 藝術地下） |
| **第一章** | 第一首歌怎麼做？三條分支，決定第二章主路線 |
| **第二章** | 依路線進入 **2A 爆紅**、**2B 穩定成長** 或 **2C 地下黑暗** |
| **第三章** | 依累積的 **名氣** 與 **形象** 進入不同分支劇情 |
| **結局** | 依最終六項數值判定五種結局之一 |

### 玩家數值（0～100）

| 數值 | 說明 |
|------|------|
| **名氣** | 曝光度、話題性 |
| **形象** | 大眾與媒體對你的觀感 |
| **健康** | 體力與精神狀態 |
| **金錢** | 資源與商業機會 |
| **自我認同** | 是否仍做「真正的自己」 |
| **爭議度** | 輿論風波與話題兩極化程度 |

每次重要抉擇都會增減上述數值；右側面板即時顯示，並搭配模擬 **社群留言** 呈現外界反應。

### 第一章 → 第二章路線

| 第一章選項 | 第二章 |
|------------|--------|
| 交給公司製作 | **2B 穩定成長線** |
| 自己創作 | 成功（約 50%）→ **2A 爆紅**；失敗 → **2C 地下黑暗** |
| 與神秘製作人合作 | **2C 地下黑暗**（並開啟隱藏「星辰議會」相關劇情） |

### 第二章各路線摘要

**2A 爆紅路線**（有插圖）
- 爆紅後安排巡演：高強度 vs 精緻小型
- 晚會訪談引發公關危機：道歉 / 發聲明 / 冷處理

**2B 穩定成長線**（有插圖）
- 首張專輯方向：商業 A&R / 個人概念 / 拒絕公司自己摸索
- 商業或概念專輯成功後，面臨「太可預測」或「報酬率太低」的二次抉擇

**2C 地下黑暗線**（目前為文字劇情）
- 歌曲病毒式爆紅後：商業化 / 堅持地下 / 操作輿論
- 若第一章曾與神秘製作人合作，可觸發 **星辰議會** 隱藏事件

### 第三章分支

依 **形象** 與 **名氣** 自動分流：

| 條件 | 分支 |
|------|------|
| 形象 ≤ 40 | 爭議巨星路線 |
| 名氣 ≥ 75 且形象 ≥ 55 | 全球偶像路線 |
| 其餘 | 成熟實力派路線 |

各分支再提供 2 個選項，影響最終數值後進入結局判定。

### 結局（五種）

| 結局 | 大致條件 |
|------|----------|
| **POP ICON：商業神話** | 名氣 ≥ 85、形象 ≥ 55、爭議度 ≤ 60 |
| **CONTROVERSIAL LEGEND：爭議巨星** | 名氣 ≥ 80、形象 ≤ 45、爭議度 ≥ 40 |
| **ARTISTIC ICON：藝術傳奇** | 形象 ≥ 80、名氣 ≥ 55、自我認同 ≥ 60 |
| **FALLEN STAR：隕落巨星** | 名氣 < 20 或 健康 ≤ 10 |
| **INDUSTRY SURVIVOR：產業倖存者** | 不符合以上特殊條件時的預設結局 |

結局畫面會顯示最終數值摘要（含城市、風格、路線、是否觸發神秘製作人線），可點 **重新開始** 再玩一次。

### 視覺小說模式（插圖章節）

第一章與第二章 A/B 已整合 **場景插圖 + 對照旁白**：

- 依「繼續」推進多格劇情
- 關鍵節點出現選項分支
- 旁白文字讀自 `image/` 資料夾內的 **圖片文本對照** 檔，並代入玩家選擇的城市、風格

---

## 技術說明

### 技術棧

| 項目 | 說明 |
|------|------|
| **語言** | Python 3.10+（建議 3.12） |
| **GUI 框架** | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 5.x — 基於 Tkinter 的現代化深色主題介面 |
| **底層視窗** | Tkinter / Tcl-Tk（Python 標準函式庫） |
| **圖片處理** | [Pillow](https://python-pillow.org/) — 載入、縮放 JPG 場景插圖，供 `CTkImage` 顯示 |
| **依賴管理** | `requirements.txt` + `pip` |

### 專案結構

```
114-2PBC_final_project/
├── main.py              # 主程式：GUI、遊戲流程、數值系統、結局判定
├── requirements.txt     # customtkinter, Pillow
├── README.md
├── image/               # 美術與劇本文本資源
│   ├── readme.txt
│   └── Pop_Idol_Base/
│       ├── CH1/         # 第一章（引言 + 三路分支）
│       ├── CH2/
│       │   ├── 2A爆紅/
│       │   └── 2B穩定成長/
│       ├── 2C黑暗/      # 2C 素材（程式整合中）
│       └── 結局/
└── old/                 # 早期原型（CLI / Pygame / 純 Tk 等）
```

### 程式架構（`main.py`）

- **`GlobalStarApp(ctk.CTk)`**：單一主視窗類別，負責介面配置與全流程控制
- **玩家狀態 `player` 字典**：集中管理 city、style、六項數值、route、hidden_producer 等
- **流程方法**：`show_start` → `show_city_selection` → `show_style_selection` → `show_chapter1` → `show_chapter2` → `show_chapter3` → `show_ending`
- **視覺場景 API**：
  - `show_visual_scene()` — 單格插圖 + 旁白 + 可選「繼續」
  - `_play_scene_sequence()` — 依序播放多格場景（第一章 / 2A / 2B 共用）
  - `show_scene()` / `show_result_scene()` — 純文字場景（第三章、部分過場）
- **資源載入**：
  - `load_story_map()` — 解析 `圖片文本對照*.txt`（以三位數編號分段）
  - `ch1_image_path()` / `ch2a_image_path()` / `ch2b_image_path()` — 依場景 ID 對應 JPG 路徑
  - `format_narrative()` — 替換 `{city_name}`、`{style}` 等佔位符

### 介面配置

- **左側**：場景插圖（有圖時顯示）+ 故事文字區（`CTkTextbox`）
- **右側**：六項數值狀態面板
- **下方**：抉擇按鈕區 + 社群反應區

視窗預設約 `1180×820`，支援深色主題（`dark-blue` color theme）。

### 資產格式約定

- 圖片：`NNN.jpg`（三位數編號，如 `016.jpg`）
- 旁白：`圖片文本對照*.txt`，格式為「編號一行 → 下方多行正文 → 下一編號」
- 出道風格規劃為 Rebel / Pop Idol / Indie 三套美術；目前 **Pop Idol** 路線資源最完整

### 設計特點

- **資料與邏輯分離**：劇情文本、圖片路徑放在 `image/`，程式以編號映射讀取，方便美術/劇本迭代
- **分支路由**：第一章 `route`（`rising` / `stable` / `hidden`）決定第二章；第三章依數值門檻分流
- **狀態驅動結局**：`compute_ending()` 依多維門檻（名氣、形象、健康、爭議度、自我認同）計算結局，鼓勵多周目探索

---

## 疑難排解

### `ModuleNotFoundError: No module named '_tkinter'`

代表目前的 Python 未內建 **Tk**。在 macOS 上若使用 Homebrew 的 Python，可改安裝內建 Tcl/Tk 的官方版本，或安裝對應版本的 `python-tk`；在 Linux 上通常需安裝 `python3-tk`（套件名稱依發行版而異）。

### `ImportError: PIL.Image couldn't be imported`

場景插圖需要 Pillow，請確認已安裝：

```bash
pip install -r requirements.txt
```

### 按鈕有反應但畫面不更新

請確認使用最新版 `main.py`，並完全關閉後重新執行 `python main.py`。若終端出現 `TclError: image "pyimage..." doesn't exist`，代表需更新至已修正插圖清除邏輯的版本。

---

## 其他原型

`old/` 資料夾內保留早期版本（如 `global_star_cli.py`、`global_star_pygame.py` 等），需另行安裝對應套件，**非本 README 主要執行入口**。正式遊玩請以 `python main.py` 為準。
