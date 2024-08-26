## 製作目的  
透過自動化定期抓取元智大學官網上的最新消息和公告，減少手動查詢的時間和精力，了解學校的最新動態。 
## Secret 使用說明  
將<code>SENDER_EMAIL</code>、<code>RECEIVER_EMAIL</code>、<code>GMAIL_PASSWORD</code>三個Secrets儲存在GitHub。  
Settings → Secrets and variables → Actions → New repository secret  
![image](https://github.com/sunnyliuaviation/Yzu_Web_Crawler/blob/main/image/Action%20Secret.png)  
Name 填入<code>SENDER_EMAIL</code>, Secret 填入要"傳送"訊息的電子郵件。    
Name 填入<code>RECEIVER_EMAIL</code>, Secret 填入要"接收"訊息的電子郵件。    
Name 填入<code>GMAIL_PASSWORD</code>, Secret 填入要傳送訊息電子郵件的密碼。gmail 需開啟兩步驟驗證的應用程式密碼，並將應用程式密碼貼到 Secret。  
接著按下 Add secret , 完成設定。  
## 未來研究目標
使用 Google Sheets 作為資料管理平台，記錄每次擷取的最新消息和公告，以便於查詢和檢索，並將擷取到的資料與 Google Sheets 中已有的數據進行比對，確保系統紀錄入未曾擷取過的資訊，解決收到重複訊息的問題。
## 參考資料  
* [【 Python 爬蟲 】2 小時初學者課程 ：一次學會 PTT 爬蟲、Hahow 爬蟲、Yahoo 電影爬蟲！](https://youtu.be/1PHp1prsxIM?si=YkFFE6DzUZQ8oPwH)  
* [【python】selenium 網頁自動化、網路爬蟲 ｜ 爬蟲 ｜ python 爬蟲 ｜ 自動化 ｜pycharm ｜](https://youtu.be/ximjGyZ93YQ?si=_wYaRLTHsVZJkxzn)  
* [Python Email 發送電子郵件 - 基本教學 By 彭彭](https://youtu.be/YQboCnlOb6Y?si=pBur5hFW7SdFT3aI)
* [GitHub Action YAML 撰寫技巧 - 環境變數(Environment Variables) 與 秘密 (Secrets)](https://ithelp.ithome.com.tw/articles/10263300)  
<p align="center">
  <strong>爬蟲資料擷取自<a href="https://www.yzu.edu.tw/index.php/tw/">元智大學</a>官網<strong>
</p>
