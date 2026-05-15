# GLOBAL STAR：成名之路

以 Python 與 **CustomTkinter** 製作的簡易 GUI 敘事模擬遊戲 MVP。玩家扮演剛簽約的新人歌手，透過城市、風格與一連串抉擇累積名氣、形象、健康等數值，並依最終狀態解鎖不同結局。

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 執行遊戲

```bash
python main.py
```

## 遊戲簡介

- 文字敘事搭配 2～4 個選項，影響名氣、形象、健康、金錢、自我認同與爭議度。
- 每個重要選擇後會顯示模擬社群留言。
- 含多條第二章路線與多種結局；若曾與神秘製作人合作，第二章會出現與「星辰議會」相關的暗示段落。
- 結局畫面可點選「重新開始」再玩一次。

專案中若還有其他示範腳本（例如 `global_star_pygame.py`），需另行安裝 `pygame` 等套件。

## 疑難排解（Tk / CustomTkinter）

若出現 `ModuleNotFoundError: No module named '_tkinter'`，代表目前的 Python 未內建 **Tk**。在 macOS 上若使用 Homebrew 的 Python，可改安裝內建 Tcl/Tk 的官方版本，或安裝對應版本的 `python-tk` 套件；在 Linux 上通常需安裝 `python3-tk`（套件名稱依發行版而異）。
