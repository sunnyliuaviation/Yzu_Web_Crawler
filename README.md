## 研究動機
隨著訊息化時代的到來，網絡資訊的更新速度日益加快，學校及各行政單位的公告、通知和最新消息通常都會在官網上發佈。對於我身為學生而言，定期查閱這些最新的重要資訊是非常重要的。然而，由於資訊更新頻繁，若依賴手動查詢，不僅耗費大量時間與精力，也容易錯過關鍵的訊息，因此想製作一個網頁爬蟲來抓取最新消息。  
## 製作目標  
* **自動化**：每天自動抓取元智大學首頁的公告，節省手動查詢時間。
* **儲存資料**：將公告的標題、連結、日期儲存到 Google Sheets，以避免重複抓取。
* **郵件通知**：發現新公告後，自動寄送通知郵件給自己。
## 學習方法
1. 構思「需求」(我希望這個爬蟲能協助我抓取到哪些資訊，並如何整理)。
2. 開始製作，透過網路資源，如: Youtube 、 Google 等網路教學學習來撰寫程式碼。
3. 過程中遇到許多報錯，若遇到無法解決的問題則向 ChatGPT 尋求協助。
## 爬蟲重點
1. 抓取元智大學首頁的訊息公告。路徑: 元智大學首頁 → 最新消息 → 公告。
2. 將抓取下來的公告儲存到 Google Sheet 中，以便在下次抓取公告時，透過比對 URL 來確認該公告是否已經抓取。
3. 經比對後，已抓取過的公告不再抓取；未抓取過的公告則儲存到 Google Sheet 中，並使用 Gmail 傳送到自己的信箱。
## 製作步驟
### 程式設計邏輯
![image](https://github.com/sunnyliuaviation/Yzu_Web_Crawler/blob/main/image/flow%20chart.png)
### Step 1: 設置環境
1. 使用 Visual Studio Code ，Python 版本為3.11.8
2. 安裝套件
   ```python
   pip install requests beautifulsoup4 smtplib gspread oauth2client
   ```
   這些套件分別用來:
   * <code>requests</code>：發送 HTTP 請求
   * <code>beautifulsoup4</code>：解析 HTML 網頁
   * <code>smtplib</code>：發送郵件
   * <code>gspread</code>：操作 Google Sheets
   * <code>oauth2client</code>：處理 Google API 認證
### Step 2: 撰寫爬蟲程式
1. **設定環境變數**
   ```python
   import os
   import requests
   from bs4 import BeautifulSoup
   import smtplib
   from email.mime.multipart import MIMEMultipart
   from email.mime.text import MIMEText
   import json
   import gspread
   from oauth2client.service_account import ServiceAccountCredentials
   
   # 讀取環境變數 (從 GitHub Secrets)
   sender_email = os.environ['SENDER_EMAIL']
   receiver_email = os.environ['RECEIVER_EMAIL']
   password = os.environ['GMAIL_PASSWORD']
   spreadsheet_id = os.environ['SPREADSHEET_ID']
   
   # 讀取存於 GitHub Secrets 中的 Google Sheets 憑證 (JSON)
   credentials_json_str = os.environ['GOOGLE_CREDENTIALS_JSON']
   credentials_info = json.loads(credentials_json_str)
   ```
2. **Google Sheets API 認證**
   ```python
      # 設定 Google Sheets API 的認證範圍
      scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
      creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
      client = gspread.authorize(creds)
      
      # 開啟 Google Sheets 文件
      sheet = client.open_by_key(spreadsheet_id).sheet1  # 獲取第一個工作表
   ```
3. **模擬使用者發出的 HTTP GET 請求，抓取網頁內容，並檢查回應狀態**   
   使用 <code>requests.get()</code> 向元智大學的首頁發送 HTTP GET 請求，並使用 <code>headers</code> 模擬瀏覽器的請求，以避免網站屏蔽自動爬蟲（某些網站可能會檢查請求頭，來確保訪問者是使用瀏覽器的真實使用者）。<code>url_page</code> 變數則用來保存網站的基礎 URL，以後面用來組合完整的連結。
   ```python
      # 模擬使用者發出的 HTTP GET 請求到伺服器端獲取網頁內容
      headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
      }
      
      url = 'https://www.yzu.edu.tw/index.php/tw'
      url_page = url[:url.find('/', url.find('//') + 2)]
      
      # 發送 HTTP GET 請求並獲取伺服器端回應
      response = requests.get(url, headers=headers)
      
      if response.status_code == 200:
          soup = BeautifulSoup(response.text, 'html.parser')
      
          # 找到所有 class 為 'msg-content' 的 div 元素
          content_divs = soup.find_all('div', class_='msg-content')
    ```
4. **公告儲存到 Google Sheet**  
   確認是否以擷取過該訊息，若無，則將該則公告儲存到 Google Sheet。      
    ```python
        email_content = ""
        if len(sheet.get_all_values()) == 0:
            sheet.append_row(['Title', 'Link', 'Date'])
    
        existing_links = [row[1] for row in sheet.get_all_values() if len(row) > 1]
    
        for content_div in content_divs:
            title_tag = content_div.find('h3').find('a')
            title = title_tag.text.strip() if title_tag else 'N/A'
            link = url_page + title_tag['href'] if title_tag and 'href' in title_tag.attrs else 'N/A'
    
            if link in existing_links:
                continue
    
            date_tag = content_div.find('div', class_='date')
            date = date_tag.text.strip() if date_tag else 'N/A'
    
            entry = f"Title: {title}\nLink: {link}\nDate: {date}\n\n"
            email_content += entry
    
            sheet.append_row([title, link, date])
            existing_links.append(link)
      ```
5. **寄送郵件通知**  
   建立郵件內容。    
      ```python
          # 寄送郵件通知
          if email_content:
              msg = MIMEMultipart()
              msg['From'] = sender_email
              msg['To'] = receiver_email
              msg['Subject'] = '[Run Crawler] 元智大學'
      
              msg.attach(MIMEText(email_content, 'plain'))
      ```
    透過 SMTP_SSL 發送郵件
      ```python
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                    print('郵件已成功寄送')
            except Exception as e:
                print(f"Error: 無法寄送郵件 - {e}")
      ```
    * <code>smtplib.SMTP_SSL()</code>：透過 Gmail 的 SMTP 伺服器發送郵件，並且使用 SSL 進行加密（Gmail 的 SSL 端口為 465）。
    * <code>server.login(sender_email, password)</code>：使用 <code>sender_email</code> 和 Gmail 的應用程式密碼進行登入驗證(必須在 Gmail 中啟用了兩步驟驗證，並生成應用程式密碼)。
    * <code>server.sendmail()</code>：這行程式負責發送郵件，從 <code>sender_email</code> 發送至 <code>receiver_email</code>，並將郵件內容格式化為字串。
### Step 3: Google Sheets API 設定
1. 建立 Google Cloud 專案並啟用 Google Sheets API
   登入 [Google Cloud Console](https://cloud.google.com/cloud-console/?utm_source=google&utm_medium=cpc&utm_campaign=japac-TW-all-zh-dr-BKWS-all-lv-trial-PHR-dr-1605216&utm_content=text-ad-none-none-DEV_c-CRE_622018104156-ADGP_Hybrid+%7C+BKWS+-+BRO+%7C+Txt+-Management+Tools-Cloud+Console-google+cloud+console-main-KWID_43700076521325430-kwd-296393718382&userloc_9197990-network_g&utm_term=KW_google%20cloud%20console&gad_source=1&gclid=EAIaIQobChMI6M-9pbKwigMVhRF7Bx0NkxRWEAAYASAAEgIuDfD_BwE&gclsrc=aw.ds) ，創建一個新專案，並啟用 Google Sheets API 和 Google Drive API，然後在 API 介面建立一個 Service Account，並下載其憑證檔案（JSON）。
2. 將憑證儲存到 GitHub Secrets
   為了避免敏感資訊外流，因此將敏感資訊存於 GitHub Secrets:
   * SENDER_EMAIL：寄件人的 Gmail 帳號
   * RECEIVER_EMAIL：收件人的 Gmail 帳號
   * GMAIL_PASSWORD：寄件人的 Gmail 密碼（Google 兩步驟驗證應用程式密碼）
   * SPREADSHEET_ID：Google Sheets 的 ID（從網址中取得）
   * GOOGLE_CREDENTIALS_JSON：下載的 Service Account 憑證內容，以字串形式儲存
### Step 4: 自動化運行爬蟲
1. 撰寫 GitHub Actions 檔案
   在專案目錄的 <code>.github/workflows</code> 目錄下，新增一個 <code>.yml</code> 檔案，例如 yzu_web_crawler.yml。(完整程式碼在[yzu_web_crawler.yml](https://github.com/sunnyliuaviation/Yzu_Web_Crawler/blob/main/.github/workflows/yzu_web_crawler.yml))
## Secret 使用說明  
將<code>SENDER_EMAIL</code>、<code>RECEIVER_EMAIL</code>、<code>GMAIL_PASSWORD</code>等五個 Secrets 儲存在 GitHub。  
Settings → Secrets and variables → Actions → New repository secret  
![image](https://github.com/sunnyliuaviation/Yzu_Web_Crawler/blob/main/image/Action%20Secret.png)  
Name 填入<code>SENDER_EMAIL</code>, Secret 填入要"傳送"訊息的電子郵件。    
Name 填入<code>RECEIVER_EMAIL</code>, Secret 填入要"接收"訊息的電子郵件。    
Name 填入<code>GMAIL_PASSWORD</code>, Secret 填入要傳送訊息電子郵件的密碼。gmail 需開啟兩步驟驗證的應用程式密碼，並將應用程式密碼貼到 Secret。  
接著按下 Add secret , 完成設定。  
## 遇到的困難及如何解決
1. 由於這次不單單只有做爬蟲，也要將抓取下來的公告透過 Gmail 寄送，還有將資料儲存到 Google Sheet 的部分，需要用到 API 串接，因此複雜度上升。於是我先將這個專案分成三個部份來製作，分別是網頁爬蟲、寄送郵件以及儲存資料並進行比對，等到三個部分都學會後，再將三個部分程式碼融合再一起，這樣對我來說學習起來相對容易。
2. 在製作這個爬蟲時，經常遇到報錯，且如果單從 Google 上找尋資料，也較難將錯誤完全排除，且身邊也沒有擁有相關知識背景的人能詢問。因此，我透過 ChatGPT 的協助，來幫助我除錯，同時，自己也進行不斷的摸索。
## 學習心得
原本就對製作 Python 網頁爬蟲感興趣的我，透過這次製作爬蟲的經驗，我學到了如何將網頁爬蟲技術、Google Sheets API 以及 Gmail SMTP 整合起來，實現一個自動化的資訊抓取與通知系統。我認為，將專案分為爬取網頁、寄送郵件、儲存資料三個部分進行，是一個有效的學習策略，讓我能逐步掌握每一個技術環節，最終成功地完成了整合，我也發現網路的資源非常龐大，透過自己摸索、查詢資料的過程，使我累積經驗，知道如何掌握查詢想要資訊的關鍵字，找到我需要的資源與資訊。過程中，雖然遇到了許多挑戰，如 API 串接、錯誤處理等，但在 ChatGPT 的協助下，我順利排除了各種錯誤，最後總共花了約三個月的時間，完成這個專案。
## 改善及建議
1. **資料儲存與查詢優化**: 目前的資料儲存在 Google Sheet 上，這對於小規模的資料管理是有效的。但如果公告數量增加，Google Sheet 的查詢效率可能會下降。日後考慮使用如 Firebase、SQL 等更強大的資料庫進行儲存，以便能有效管理大量數據。
2. **公告過濾與分類**: 除了目前的爬取公告功能，未來可以加入公告的過濾或分類功能，根據不同的關鍵字、類別來進行篩選。例如，根據公告的標題或內容篩選出學術、課程相關或校內活動等特定類別，可以更快速得到需要的資訊。
## 待解決的問題
在公告儲存時，有些連結並沒有轉成超連結，如下圖:  
![image](https://github.com/sunnyliuaviation/Yzu_Web_Crawler/blob/main/image/Google%20Sheet.png)
## 參考資料  
* [【 Python 爬蟲 】2 小時初學者課程 ：一次學會 PTT 爬蟲、Hahow 爬蟲、Yahoo 電影爬蟲！](https://youtu.be/1PHp1prsxIM?si=YkFFE6DzUZQ8oPwH)  
* [【python】selenium 網頁自動化、網路爬蟲 ｜ 爬蟲 ｜ python 爬蟲 ｜ 自動化 ｜pycharm ｜](https://youtu.be/ximjGyZ93YQ?si=_wYaRLTHsVZJkxzn)  
* [Python Email 發送電子郵件 - 基本教學 By 彭彭](https://youtu.be/YQboCnlOb6Y?si=pBur5hFW7SdFT3aI)
* [GitHub Action YAML 撰寫技巧 - 環境變數(Environment Variables) 與 秘密 (Secrets)](https://ithelp.ithome.com.tw/articles/10263300)  
<p align="center">
  <strong>爬蟲資料擷取自<a href="https://www.yzu.edu.tw/index.php/tw/">元智大學</a>官網<strong>
</p>
