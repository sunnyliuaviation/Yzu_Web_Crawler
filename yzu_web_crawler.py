import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 寄送郵件的設定
sender_email = os.environ['SENDER_EMAIL']
receiver_email = os.environ['RECEIVER_EMAIL']
password = os.environ['GMAIL_PASSWORD']

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

    # 逐一處理每個找到的 div 元素
    for content_div in content_divs:
        # 找到標題的 a 標籤
        title_tag = content_div.find('h3').find('a')
        title = title_tag.text.strip() if title_tag else 'N/A'

        # 組合完整的連結 URL，如果找到標籤中的 href 屬性
        link = url_page + title_tag['href'] if title_tag and 'href' in title_tag.attrs else 'N/A'

        # 找到日期
        date_tag = content_div.find('div', class_='date')
        date = date_tag.text.strip() if date_tag else 'N/A'

        # 構建每個條目的格式
        entry = f"Title: {title}\nLink: {link}\nDate: {date}\n\n"
        email_content += entry

    # 建立郵件物件
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
    print('沒抓到網頁')
