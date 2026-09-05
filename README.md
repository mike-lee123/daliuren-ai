# 玄機閣 · 大六壬起課

Streamlit 應用程式：輸入事由與時間後自動排大六壬課、繪製命盤圖片，並產出可貼進 ChatGPT / Grok / DeepSeek 的 AI 提示詞。

佈署後網址：<https://daliuren-ai.streamlit.app>

## 檔案說明

| 檔案 | 用途 |
| --- | --- |
| `app.py` | 主程式 |
| `requirements.txt` | Python 套件 |
| `packages.txt` | Streamlit Cloud 的系統套件（安裝中文字型 `fonts-noto-cjk`，命盤圖片才有中文） |
| `.streamlit/config.toml` | 佈景設定（選用） |

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 佈署到 Streamlit Community Cloud（免費、永久網址）

1. 到 <https://github.com/new> 建立一個 repo（可設為 Public 或 Private），把本資料夾所有檔案上傳／推送上去。
2. 前往 <https://share.streamlit.io>，用 GitHub 帳號登入。
3. 點 **Create app** → **Deploy a public app from GitHub**。
4. 選擇：
   - Repository：剛才建立的 repo
   - Branch：`main`
   - Main file path：`app.py`
   - App URL：`daliuren-ai`（產生 `https://daliuren-ai.streamlit.app`；若被占用可改 `daliuren-ai-tw`、`daliuren-ai-app`）
5. （選用）在 **Advanced settings** 把 Python version 設為 3.11。
6. 按 **Deploy**，等待數分鐘建置完成。

完成後會得到 `https://daliuren-ai.streamlit.app` 的永久網址，只要 repo 還在、帳號正常，網址就一直有效；每次 push 到 `main` 會自動重新佈署。

> 注意：免費方案的 App 若連續數天無人造訪會進入休眠，下次有人開啟時會自動喚醒（約需 30 秒），網址不會改變。
