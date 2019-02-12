# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from Download1024.settings import  ROOT_URL
import re
from scrapy import Request
import  os

class SmilespiderSpider(scrapy.Spider):
    root_url = ROOT_URL
    name = 'SmileSpider'
    allowed_domains = ['t66y.com']
    start_urls = ['http://t66y.com/thread0806.php?fid=16&search=&page=1']
    local_file_dir='D:/my1024pic/'
    def parse(self, response):
        content = response.body
        soup_handler = BeautifulSoup(content,"html.parser")
        template_article_list = soup_handler.find_all('a',attrs={"href":True,"id":True})
        next_urls_list = soup_handler.find_all('a',string="下一頁")
        last_urls_list  = soup_handler.find_all('a',attrs={"id":"last"})
        next_urls = self.root_url + next_urls_list[0]['href']
        last_urls = self.root_url + last_urls_list[0]['href']
        article_url = []
        match_reg='\w*\/\d*\/\d*\/\d*.html'
        for item in template_article_list:
            if re.match(match_reg,item['href']):
                urls = self.root_url + item['href']
                article_url.append(urls)
        for url in article_url:
            yield Request(url=url,callback=self.parse_img,meta={})
        if next_urls:
            yield Request(url=next_urls,callback=self.parse)


    def parse_img(self, response):
        img_list = []
        content = response.body
        soup_handler = BeautifulSoup(content,"html.parser")
        temp_title_list = soup_handler.find_all('h4')
        temp_img_url_list = soup_handler.find_all('input',attrs={"data-src":True})
        title_name = re.sub('\?|:','',temp_title_list[0].text)
        #print(title_name)
        for img in temp_img_url_list:
            if img['data-src']:
                img_list.append(img['data-src'])
        for img_url in img_list:
            yield Request(url=img_url,callback=self.parse_download_img,meta={'title_name':title_name,'index':img_list.index(img_url)},dont_filter=True)


    def parse_download_img(self, response):
        content = response.body
        title_name = response.meta['title_name']
        index = response.meta['index']
        img_format = response.url.split('.')[-1]
        file_dir =self.local_file_dir + title_name + '/'
        file_name = file_dir + str(index) + '.'+ img_format
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(file_name,'xb') as f:
            f.write(content)
            print('{} {} {}'.format('IMG:',response.url,'[完成]'))