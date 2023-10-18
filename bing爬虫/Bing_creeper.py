from bs4 import BeautifulSoup,Tag
import requests,json
from jinja2 import Template,Environment,FileSystemLoader
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pykakasi import kakasi
from selenium import webdriver
import re
from weasyprint import HTML
import pdfkit
#import qrcode
from PIL import Image
import base64

class BingCreeper():
    def __init__(self,url:str) -> None:
        """_summary_

        Args:
            url (str): bing新闻网址
        """
        self.url = url
        self.get_web_content()
        self.render_html()
        self.printPDF()

        
        
    def get_web_content(self) -> None:
        self.driver = webdriver.Edge()
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 5)
        # 设置等待条件，等待名为'consumption-feed-content'的div元素可见
        content_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'consumption-feed-content')))
        # 获取整个页面的HTML内容
        self.origin_page_source = self.driver.page_source
        self.driver.quit()
        self.soup = BeautifulSoup(self.origin_page_source,'html.parser')
        self.news_title = self.soup.find('title').text
        self.content_code = self.soup.find(name='div', attrs={'class': 'consumption-feed-content'}).attrs['data-content-id']
        self.second_page_source = requests.get('https://assets.msn.com/content/view/v2/Detail/ja-jp/'+self.content_code)
        self.article_dict = json.loads(self.second_page_source.text)
        # self.article_abstract = self.article_dict['abstract']
        soup = BeautifulSoup(self.article_dict['body'],'html.parser')
        article_content = soup.find_all('p') #列表 里面是是p标签 长度为文章段数 
        self.article_content =[i.text for i in article_content]
        self.article_date = self.article_dict['publishedDateTime'].split('T')[0]
        self.article_cover = self.article_dict['imageResources'][1]['url']
                
        self.news = News_article(title=self.news_title,
                            author=self.article_dict['authors'][0]['name'],
                            content=self.article_content,
                            date=self.article_date,
                            cover=self.article_cover)
        self.decorate_content()

        
    def decorate_content(self) -> None:
        self.kakasi_instance = kakasi()
        self.decorate_content = []
        self.decorate_title = []
        for i in self.news.content:
            converted_text = self.kakasi_instance.convert(i)
            after_text=''
            for i in converted_text:
                if i['orig'] == i['hira']:
                    after_text += i['orig']
                else:
                    after_text += '<ruby>'+i['orig']+'<rt>'+i['hira']+'</rt></ruby>'
            after_text += ''
            self.decorate_content.append(after_text)
        self.news.content = self.decorate_content
        
        tmp=''
        for i in self.news.title:
            
            converted_text = self.kakasi_instance.convert(i)
            after_text=''
            for i in converted_text:
                if i['orig'] == i['hira']:
                    after_text += i['orig']
                else:
                    after_text += '<ruby>'+i['orig']+'<rt>'+i['hira']+'</rt></ruby>'
            tmp += after_text
        self.news.title = tmp
            
    def render_html(self):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('./src/bing_news_template.html')
        # 渲染模板并生成临时 HTML 文件
        rendered_html = template.render(data = self.news)
        self.render_html_dir = './src/'+self.news.date+'_'+self.news.author+'.html'
        with open(self.render_html_dir, 'w') as file:
            file.write(rendered_html)
            
    
        
            
    def printPDF(self):

        # 使用 WeasyPrint 打印 HTML
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdf_path = './'+self.news.author+self.news.date+'output.pdf'
        options = {
        'no-stop-slow-scripts': None,
        'image-quality': '100',
        'enable-local-file-access': None,
        'margin-top': '0',
        'page-size': 'A4',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        'encoding': "UTF-8",}
        pdfkit.from_file(self.render_html_dir, pdf_path,configuration=config,options=options) 
        
    def QRcode_img(self):
        # 生成二维码
        url = "http://iibread.xyz/player/index.html?date="+self.date
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color=(255, 255, 255, 0))
        # 将白色部分变成透明底
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        # 保存图像
        img.save('qrcode.png', "PNG")
        # 打开图像文件
        with open("qrcode.png", "rb") as image_file:
            # 读取图像文件内容
            image_data = image_file.read()
            # 将图像内容转换为base64编码
            base64_data = base64.b64encode(image_data).decode('utf-8')
            # 打印base64编码
            self.base64_data = base64_data
            
            



class News_article():
    def __init__(self,title:str,
                 author:str,
                 content:list,
                 date:str,
                 cover:str) -> None:
        self.title = title
        self.content = content
        self.author = author
        self.date = date
        self.cover = cover