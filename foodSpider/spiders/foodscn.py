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

class FoodScnSpider(scrapy.Spider):
    name = "foodscn";
    #custom_settings = {
    #    'ITEM_PIPELINES':{'foodSpider.pipelines.FoodScnPipeline': 101,}
    #};

    def __init__(self):
        self.urls = [
            #'http://www.foodscn.cn/news/news/',       #要闻
            #'http://www.foodscn.cn/news/jujiao/',     #聚焦
            #'http://www.foodscn.cn/news/jianguan/',   #监管
            #'http://www.foodscn.cn/news/pinpai/',     #品牌
            #'http://www.foodscn.cn/news/dujia/',      #独家
            #'http://www.foodscn.cn/news/yuqing/',     #舆情
            #'http://www.foodscn.cn/news/baoguang/',   #曝光
            #'http://www.foodscn.cn/news/huizhan/',    #会展
            #'http://www.foodscn.cn/news/zhaoshang/',  #招商
            #'http://www.foodscn.cn/news/meishi/',     #美食
            #'http://www.foodscn.cn/news/renwu/',      #人物
            #'http://www.foodscn.cn/news/weichuanbo/', #微传播
            #'http://www.foodscn.cn/news/guoji/',      #国际
        ];
        self.newsCount = 0;    #抓到的新闻条数
        self.urls_names = [
            ['news',     u'要闻'],
            ['jujiao',   u'聚焦'],
            ['jianguan', u'监管'],
            ['pinpai',   u'品牌'],
            ['dujia',    u'独家'],
            ['yuqing',   u'舆情'],
            ['baoguang', u'曝光'],
            ['huizhan',  u'会展'],
            ['zhaoshang',u'招商'],
            ['meishi',   u'美食'],
            ['renwu',    u'人物'],
            ['weichuanbo',u'微传播'],
            ['guoji',    u'国际'],
        ];

    def start_requests(self):
        for url in self.urls_names:
            link = 'http://www.foodscn.cn/news/' + url[0] + '/';
            print (link);
            yield scrapy.Request(url = link, callback = self.parse);


    def parse(self, response):
        print("....【中国安全食品网】... " + response.url);
        link = response.url + 'newslist.php?p=2';   #点第二页来找尾页
        yield scrapy.Request(url = link, callback = self.parse_found_last_lage);

        '''
        a_selectors = response.xpath("//div[@id='pages']/a[@href]");
        print (a_selectors);
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            print (text);
            if (text == '2'):
                link = selector.xpath("@href").extract_first();
                print (link);
        '''

    def parse_found_last_lage(self, response):
        print ('parse_found_last_lage ' + response.url);
        a_selectors = response.xpath("//div[@id='pages']/a[@href]");
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            if (text == u'最未页'):     #是 中国安全食品网 的程序员写错的 “最未页”
                link = selector.xpath("@href").extract_first();
                page_num_max = link.split('=')[-1];
                print ("page_num_max:", page_num_max);

                for page in range(1, int(page_num_max) + 1):
                #for page in range(1, int(2) + 1):
                    url = response.url.split('=')[0] + '=' + str(page);
                    print ('url: ' + url);
                    request = response.follow(url, callback = self.parse_get_news_title, dont_filter = True);
                    yield request;

    def parse_get_news_title(self, response):
        print('parse_get_news_details -------> ' + response.url);
        a_selectors = response.xpath("//div[@id='ncontent-left']//div[@class='newslist-title']/a");
        #print ('a_selectors:', a_selectors);
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            link = selector.xpath("@href").extract_first();
            link = 'http://www.foodscn.cn' + link;   #需要补齐url
            #print (text + " " + link);
            request = response.follow(link, callback = self.parse_news_details);
            request.meta['major'] = response.url.split('/')[-2];    #获取新闻分类
            yield request;

    #获取新闻详细信息,并保存数据
    def parse_news_details(self, response):
        #print('parse_news_details: ' + response.url);
        div_selectors = response.xpath("//div[@id='ncontent-left']");

        title = div_selectors.xpath('.//div[@id="newstitle"]/text()').extract_first(); 
        newsinfo = div_selectors.xpath('.//div[@id="newsinfo"]/text()').extract_first(); 
        #print (newsinfo.split(" ")); 
        date = newsinfo.split(" ")[0].split("：")[-1] + " " + newsinfo.split(" ")[1];
        source = newsinfo.split(" ")[2].split("：")[-1];
        content_text = "";
        contents = div_selectors.xpath('.//div[@id="newscontent"]//p');   #正文取所有段落
        if (contents == []):  #有一些正文没有p标签，只能选去全部文字
            #print ("contents is null");
            content_texts = div_selectors.xpath('.//div[@id="newscontent"]/text()').extract(); 
            for text in content_texts:
                content_text += text;  
            #print (content_text);
        else:
            for content in contents:
                content_text += content.xpath('string()').extract_first(); 
                #print (content.xpath('text()').extract_first())

        #查找新闻分类字符名字
        major = '';
        meta_major = response.meta['major'];
        for name in self.urls_names:
            if (meta_major == name[0]):
                major = name[1];
                break;

        item = FoodCfsnItem();
        item['major'] = major;
        item['title'] = title;
        item['publish'] = date;
        item['source'] = source;
        item['content'] = content_text;
        item['content_len'] = len(content_text);  #内容长度
        item['url'] = response.url;

        '''
        print ('major:', item['major']);
        print ('title:', item['title']);
        print ('source:', item['source']);
        print ('publish:', item['publish']);
        print ('content_len:', item['content_len']);
        #print ('content:', item['content']);
        print ('url:', item['url']);
        '''

        self.newsCount = self.newsCount + 1;
        print ("[%s] count %d" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.newsCount));

        yield item;










