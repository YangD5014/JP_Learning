from bs4 import BeautifulSoup,Tag
import requests,json
from jinja2 import Template,Environment,FileSystemLoader
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pykakasi import kakasi
import azure.cognitiveservices.speech as speechsdk
from selenium import webdriver
import hashlib
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
        self.generate_sound()

        
        
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
        self.article_content =[i.text for i in article_content if article_content]
        self.article_content =[i for i in self.article_content if i !='']
        
        self.article_date = self.article_dict['publishedDateTime'].split('T')[0]
        self.article_cover = self.article_dict['imageResources'][0]['url']
        
        self.news_title_translate = BingCreeper.get_traslation(translate_querry=self.news_title)
        
        self.article_content_translate = [BingCreeper.get_traslation(translate_querry=i) for i in self.article_content if i !='']
                
        self.news = News_article(title=self.news_title,
                            author=self.article_dict['authors'][0]['name'],
                            content=self.article_content,
                            date=self.article_date,
                            cover=self.article_cover,
                            title_translate=self.news_title_translate,
                            content_translate=self.article_content_translate)
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
        template = env.get_template('./src/template/读卖テレビ.html')
        # 渲染模板并生成临时 HTML 文件
        rendered_html = template.render(data = self.news)
        self.render_html_dir = './src/'+self.news.date+'_'+self.news.author+self.news_title[:10]+'.html'
        with open(self.render_html_dir, 'w') as file:
            file.write(rendered_html)
            
    
    @staticmethod
    def get_traslation(translate_querry:str)->str:
        translate_url = "http://api.fanyi.baidu.com/api/trans/vip/translate?"
        appid = '20191107000354007'
        salt='1435660288'
        appkey = 'uCqsidm6I7Ssa8aU1pgZ'
        sign = hashlib.md5((appid+translate_querry+salt+appkey).encode('utf-8')).hexdigest()
        translate_url+='q={querry}&from=jp&to=zh&appid={appid}&salt={salt}&sign={sign}'.format(querry=translate_querry,appid=appid,salt=salt,sign=sign)
        response = requests.get(translate_url)
        translation_result = response.json()['trans_result'][0]['dst']
        print(f'翻译结果是={translation_result}')
        return translation_result
    
    
    def generate_sound(self):
        speech_config = speechsdk.SpeechConfig(subscription='576c74fce86a41bdae3473085ce32be7', region='japaneast')
        audio_config = speechsdk.audio.AudioOutputConfig(filename='./src/sound/'+self.article_date+'_'+self.news.author+self.news_title[:10]+'.mp3')
        speech_config.speech_synthesis_voice_name='ja-JP-KeitaNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)   
        content = ';'.join(self.article_content)
        text = self.news_title+'.' + content
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        
            
    def printPDF(self):

        # 使用 WeasyPrint 打印 HTML
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdf_path = './'+self.news.author+self.news.date+self.news_title[:10]+'output.pdf'
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
                 cover:str,
                 title_translate:str,
                 content_translate:list) -> None:
        self.title = title
        self.content = content
        self.author = author
        self.date = date
        self.cover = cover
        self.title_translate = title_translate
        self.content_translate = content_translate