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

# 設定 Google Sheets API 的認證範圍
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
client = gspread.authorize(creds)

# 開啟 Google Sheets 文件
sheet = client.open_by_key(spreadsheet_id).sheet1  # 獲取第一個工作表

# 模擬使用者發出的 HTTP GET 請求到伺服器端獲取網頁內容
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# 目標網頁的 URL
url = 'https://www.yzu.edu.tw/index.php/tw'
url_page = url[:url.find('/', url.find('//') + 2)]

# 發送 HTTP GET 請求並獲取伺服器端回應
response = requests.get(url)

if response.status_code == 200:
    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有 class 為 'msg-content' 的 div 元素
    content_divs = soup.find_all('div', class_='msg-content')

    # 建立郵件內容的變數
    email_content = ""

    # 檢查工作表是否是空的，如果是，則加入表頭
    if len(sheet.get_all_values()) == 0:
        sheet.append_row(['Title', 'Link', 'Date'])

    # 獲取 Google Sheets 中已經儲存的所有連結
    existing_links = []
    for row in sheet.get_all_values():
        if len(row) > 1:  # 確保該行有 Link 欄位
            existing_links.append(row[1])

    # 逐一處理每個找到的 div 元素
    for content_div in content_divs:
        # 找到標題的 a 標籤
        title_tag = content_div.find('h3').find('a')
        title = title_tag.text.strip() if title_tag else 'N/A'

        # 如果找到標籤中的 href 屬性，組合完整的連結 URL
        link = url_page + title_tag['href'] if title_tag and 'href' in title_tag.attrs else 'N/A'

        # 確認資料是否已經抓取過，如果連結沒有在 Google Sheets 中，則繼續
        if link in existing_links:
            print(f"跳過已抓取過的連結: {link}")
            continue

        # 找到日期
        date_tag = content_div.find('div', class_='date')
        date = date_tag.text.strip() if date_tag else 'N/A'

        # 建構每個條目的格式
        entry = f"Title: {title}\nLink: {link}\nDate: {date}\n\n"
        email_content += entry

        # 將資料寫入 Google Sheets
        sheet.append_row([title, link, date])

        # 更新已抓取的連結列表
        existing_links.append(link)

    # 建立郵件物件
    if email_content:  # 如果有新增資料，才發送郵件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = '[Run Crawler] 元智大學'

        # 加入郵件內容
        body = email_content
        msg.attach(MIMEText(body, 'plain'))

        # 使用 SMTP_SSL 連線到 Gmail SMTP 伺服器
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print('郵件已成功寄送')
        except Exception as e:
            print(f"Error: 無法寄送郵件 - {e}")
    else:
        print('沒有新的資料可寄送郵件')
else:
    print('沒抓到網頁')
