# -*- coding: utf-8 -*-

import scrapy
import os,time
from .upload import *
from ..items import *

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "www.cfsn.cn",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15",
    "Accept-Language": "zh-cn",
    #'Accept-Encoding: gzip, deflate',
    "Connection": "keep-alive"
};

class FoodSpider(scrapy.Spider):
    name = "foodcfsn";


    def __init__(self):
        #地方 企业 两个页面不一样
        self.major_list = [u'酒业', u'饮品', u'乳业', u'婴幼', u'零食', u'茶业', u'粮油', u'糖业', u'肉畜', u'水产', u'果蔬', u'保健', u'烘培', u'调味', u'添加剂', 
            u'校园', u'电商', u'餐饮', u'商超', u'物流', u'市场', u'商旅', u'国际', u'宠物', u'检测', u'科技', u'机械包装'];

        #省份新闻 列表
        self.province_list = [
            ['1', u'北京'],
            ['2', u'天津'],
            ['3', u'河北'],
            ['4', u'山西'],
            ['5', u'内蒙古'],
            ['6', u'辽宁'],
            ['7', u'吉林'],
            ['8', u'黑龙江'],
            ['9', u'上海'],
            ['10', u'江苏'],
            ['11', u'浙江'],
            ['12', u'安徽'],
            ['13', u'福建'],
            ['14', u'江西'],
            ['15', u'山东'],
            ['16', u'河南'],
            ['17', u'湖北'],
            ['18', u'湖南'],
            ['19', u'广东'],
            ['20', u'广西'],
            ['21', u'海南'],
            ['22', u'重庆'],
            ['23', u'四川'],
            ['24', u'贵州'],
            ['25', u'云南'],
            ['26', u'西藏'],
            ['27', u'陕西'],
            ['28', u'青海'],
            ['29', u'甘肃'],
            ['30', u'宁夏'],
            ['31', u'新疆'],
            ['32', u'深圳'],
        ];
        #省份新闻首页地址通用前缀
        self.province_url_base_tjbw = 'http://www.cfsn.cn/front/web/site.tjbwlist?sjid=';
        self.sub_list_tjbw =[
            ['&tjid=4&lmid=1', u'市场监管局-新闻动态'],
            ['&tjid=4&lmid=2', u'市场监管局-通知公告'],
            ['&tjid=4&lmid=3', u'市场监管局-政策法规'],
            ['&tjid=4&lmid=4', u'市场监管局-专题活动'],
            ['&tjid=4&lmid=5', u'市场监管局-媒体聚焦'],

            ['&tjid=5&lmid=1', u'农业弄村厅-新闻动态'],
            ['&tjid=5&lmid=2', u'农业弄村厅-通知公告'],
            ['&tjid=5&lmid=3', u'农业弄村厅-政策法规'],
            ['&tjid=5&lmid=4', u'农业弄村厅-专题活动'],
            ['&tjid=5&lmid=5', u'农业弄村厅-媒体聚焦'],

            ['&tjid=6&lmid=1', u'卫健委-新闻动态'],
            ['&tjid=6&lmid=2', u'卫健委-通知公告'],
            ['&tjid=6&lmid=3', u'卫健委-政策法规'],
            ['&tjid=6&lmid=4', u'卫健委-专题活动'],
            ['&tjid=6&lmid=5', u'卫健委-媒体聚焦'],
        ];

        self.province_url_base_sheng = 'http://www.cfsn.cn/front/web/site.shenglist?sjid=';
        self.sub_list_sheng =[
            ['&lmid=4', u'区县新闻'],
            ['&lmid=5', u'产业新闻'],
            ['&lmid=7', u'舆情热点'],
            ['&lmid=8', u'人物声音'],
            ['&lmid=9', u'政策解读'],
            ['&lmid=10', u'专题活动'],];

        #self.major_list = [u'添加剂'];
        self.newsCount = 0;    #抓到的新闻条数

    def start_requests(self):
        urls = [
            'http://www.cfsn.cn',  #中国食品安全网首页
        ];
        print ("Start Time: (%s)" %time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())));
        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse, headers = header);

        #省份新闻:市场监管局,农业弄村厅,卫健委
        for pro_num in self.province_list:
            url_base =  self.province_url_base_tjbw + pro_num[0];
            for sub_url in self.sub_list_tjbw:
                url = url_base + sub_url[0];
                print (url);
                info = {};
                info['major'] = pro_num[1] + '-' + sub_url[1];
                request = scrapy.Request(url = url, callback = self.parse_province_get_page_num, headers = header);
                request.meta['info']=info;    #传递参数
                yield request;

        #省份新闻:区县新闻,产业新闻,舆情热点,人物声音,政策解读,专题活动
        for pro_num in self.province_list:
            url_base =  self.province_url_base_sheng + pro_num[0];
            for sub_url in self.sub_list_sheng:
                url = url_base + sub_url[0];
                #print (url);
                info = {};
                info['major'] = pro_num[1] + '-' + sub_url[1];
                request = scrapy.Request(url = url, callback = self.parse_province_get_page_num, headers = header);
                request.meta['info']=info;    #传递参数
                yield request;


    def parse(self, response):
        print("....【中国食品安全网】... " + response.url);
        a_selectors = response.xpath("//div[@class='nav']/div[@class='wal']//li");
        a_selectors += response.xpath("//div[@class='wal subNav']//div[@class='list']//li");
        #print (a_selectors)
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            link = selector.xpath("./a/@href").extract_first();
            #print text,link
            for major in self.major_list:
                if (text == major):
                    info = {}                #创建信息参数
                    info['major'] = text;
                    request = response.follow(link, callback = self.parse_major);
                    request.meta['info']=info;    #传递参数
                    yield request;


    def parse_major(self, response):
        info = response.meta['info'];
        #print("major:" + info['major'] + response.url);
        
        #头条
        div_selectors = response.xpath("//div[@class='indexPart2']");
        h1 = div_selectors.xpath('./h1/a');
        h1_text = h1.xpath('string()').extract_first();
        h1_link = h1.xpath('@href').extract_first();
        request = response.follow(h1_link, callback = self.parse_and_upload);
        request.meta['info']=info;    #传递参数
        yield request;

        #时政新闻和行业新闻
        a_selectors = response.xpath("//div[@class='fr list']//a");
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            link = selector.xpath("@href").extract_first();
            request = response.follow(link, callback = self.parse_and_upload);
            request.meta['info']=info;    #传递参数
            yield request;
        

        #遍历页码, 通过查找”尾页“来确定共有多少页
        page_num = 1;
        a_selectors = response.xpath('//a[contains(@href, "&page=")]');
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            if (text == u'尾页'):
                link = selector.xpath("@href").extract_first();
                page_num = link.split('=')[-1];
                print (info['major'], "共", page_num, "页");

        for page in range(1, int(page_num) + 1):
            link = response.url + "&page=" + str(page);    #拼接成url
            request = response.follow(link, callback = self.parse_page_news);
            request.meta['info'] = info; 
            yield request;


    def parse_page_news(self, response):
        info = response.meta['info'];
        a_selectors = response.xpath('//div[@class="pageList"]//div[@class="name"]/a');
        print (a_selectors)
        for selector in a_selectors:
            text = selector.xpath('text()').extract_first();
            #print (text);
            link = selector.xpath("@href").extract_first();
            request = response.follow(link, callback = self.parse_get_news_and_upload);
            request.meta['info'] = info; 
            yield request;


    def parse_header(self, response):
        info = response.meta['info'];
        #print("parse_header:" + info['major'] + response.url);
        div_selectors = response.xpath("//div[@class='fl w655 newShow']");
        head_text = div_selectors.xpath('./h2[@class="title"]/text()').extract_first();
        #head_text = head.xpath('text()').extract_first();
        date = div_selectors.xpath('./div[@class="msg"]/div/text()').extract_first();       #时间
        come = div_selectors.xpath('./div[@class="msg"]/div/span/text()').extract_first();  #源自
        content = div_selectors.xpath('./div[@class="content"]/p');
        content_text = content.xpath('string()').extract_first();


        #提取数据并上传
    def parse_get_news_and_upload(self, response):    
        info = response.meta['info'];

        div_selectors = response.xpath("//div[@class='fl w655 newShow']");
        #标题
        title = div_selectors.xpath('./h2[@class="title"]/text()').extract_first(); 
        #源自
        source = div_selectors.xpath('./div[@class="msg"]/div/span/text()').extract_first();
        source = source.split('：')[-1];
        #时间
        date = div_selectors.xpath('./div[@class="msg"]/div/text()').extract_first() + ":00";       #时间 加上秒
        #内容
        content = div_selectors.xpath('./div[@class="content"]');
        content_text = content.xpath('string()').extract_first();

        item = FoodCfsnItem();
        item['major'] = info['major'];
        item['title'] = title;
        item['publish'] = date;
        item['source'] = source;
        item['content'] = content_text;
        item['content_len'] = len(content_text);  #内容长度
        item['url'] = response.url;

        #print (item);
        #print('major:', item['major']);
        #print('title:', item['title']);

        self.newsCount = self.newsCount + 1;
        print ("[%s] count %d" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.newsCount));
        yield item;


    def parse_province_get_page_num(self, response):
        info = response.meta['info'];
        #遍历页码, 通过查找”尾页“来确定共有多少页
        page_num = 1;
        a_selectors = response.xpath('//a[contains(@href, "&page=")]');
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            if (text == u'尾页'):
                link = selector.xpath("@href").extract_first();
                page_num = link.split('=')[-1];
                print (info['major'], "共", page_num, "页");

        for page in range(1, int(page_num) + 1):
            link = response.url + "&page=" + str(page);    #拼接成url
            request = response.follow(link, callback = self.parse_province_get_title_url);
            request.meta['info'] = info; 
            yield request;
        pass;

    def parse_province_get_title_url(self, response):
        info = response.meta['info'];
        a_selectors = response.xpath('//div[@class="news"]//li/a[@href]');
        for selector in a_selectors:
            text = selector.xpath('text()').extract_first();
            #print (text);
            link = selector.xpath("@href").extract_first();
            request = response.follow(link, callback = self.parse_get_news_and_upload);
            request.meta['info'] = info; 
            yield request;
