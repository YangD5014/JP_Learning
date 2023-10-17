from bs4 import BeautifulSoup,Tag
import requests,json
from jinja2 import Template,Environment,FileSystemLoader
import re
from weasyprint import HTML
import pdfkit
import qrcode
from PIL import Image
import base64

class NHK_creeper():
    def __init__(self,url:str,date:str) -> None:
        """_summary_

        Args:
            url (string): NHK 网站上的网址
            file_name (string): 文件夹下的文件名(最好是地区名 如 池袋站)
        """
        self.url = url
        self.response = requests.get(url=self.url)
        self.response.encoding = 'utf-8'
        self.date = date
        self.soup = BeautifulSoup(self.response.text,'html.parser')
        self.file_path = r'D:\爬虫\NHK新闻'+f'\{self.date}'
        self.get_nhk_news()
        
    def get_nhk_news(self) -> None:
        #标题收集
        self.title = ''
        h1_tag = self.soup.find('h1', class_='article-main__title')
        for each_item in h1_tag.contents:
            self.simple_titile = h1_tag.get_text(strip=True)
            if type(each_item) is Tag:
                self.title += each_item.decode()
            else:
                self.title += each_item.get_text(strip=True)
        print(f'title={self.title}')
        
        self.pattern = r'<\/?(?:span|p|a)[^>]*>'
        #内容收集
        text = self.soup.select('.article-main__body')
        p_set = self.soup.find(id='js-article-body').find_all('p') #p_set是一个列表 元素个数对应段数
        self.paragraphs=[]
        self.simple_paragraphs=[]
        for each_paragrah in p_set:
            self.simple_paragraphs.append(each_paragrah.get_text(strip=True))
            string = each_paragrah.decode()
            result = re.sub(self.pattern, '', string)
            self.paragraphs.append(result)
        
        
        self.QRcode_img()
        self.web_content= {"Title":self.title}
        self.web_content['Content'] = {"Paragraph"+str(index+1):content for index,content in enumerate(self.paragraphs)}
        self.web_content['SimpleContent'] = {"Paragraph"+str(index+1):content for index,content in enumerate(self.simple_paragraphs)}
        self.web_content['SimpleTitle'] = self.simple_titile
        self.web_content['Date'] = self.date
        self.web_content['ImageBase64'] = self.base64_data
        
        #将获取到的数据打包成json文件
        with open('./src/NHK_news'+self.date+'.json','w',encoding='utf-8') as f:
            json.dump(self.web_content,f,ensure_ascii=False)
        
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('./src/template.html')
        # 渲染模板并生成临时 HTML 文件
        rendered_html = template.render(data = self.web_content)
        with open('./bind'+self.date+'.html', 'w') as file:
            file.write(rendered_html)
            
    def printPDF(self):

        # 使用 WeasyPrint 打印 HTML
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdf_path = self.date+'output.pdf'
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
        pdfkit.from_file('./bind'+self.date+'.html', pdf_path,configuration=config,options=options) 
        
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