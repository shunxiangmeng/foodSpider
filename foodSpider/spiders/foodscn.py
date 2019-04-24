# -*- coding: utf-8 -*-

import scrapy
import os,time
import re
from ..items import *

SEARCH_PAGE_MAX = 10;  #增量更新，只查前10页的内容

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
        self.picsCount = 0;    #下载的照片数量
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
            ['shiping'   u'食评'],
        ];

    def start_requests(self):
       	"""
        url = 'http://www.foodscn.cn/news/2019/04/12/155503878526.htm';
        request = scrapy.Request(url = url, callback = self.parse_news_details);
        request.meta['major'] = 'test';
        yield request;
        """

        for url in self.urls_names:
            link = 'http://www.foodscn.cn/news/' + url[0] + '/';
            #print (link);
            yield scrapy.Request(url = link, callback = self.parse);
        #"""
        

    def parse(self, response):
        print("....【中国安全食品网】... " + response.url);
        link = response.url + 'newslist.php?p=2';   #点第二页来找尾页
        yield scrapy.Request(url = link, callback = self.parse_found_last_lage);


    def parse_found_last_lage(self, response):
        print ('parse_found_last_lage ' + response.url);
        a_selectors = response.xpath("//div[@id='pages']/a[@href]");
        for selector in a_selectors:
            text = selector.xpath("string()").extract_first();
            if (text == u'最未页'):     #是 中国安全食品网 的程序员写错的 “最未页”
                link = selector.xpath("@href").extract_first();
                page_num_max = int(link.split('=')[-1]);
                #数据更新，太老的数据不用重复爬取
                if (page_num_max >= SEARCH_PAGE_MAX):
                	page_num_max = SEARCH_PAGE_MAX;
                print ("page_num_max:", page_num_max);
                for page in range(1, page_num_max + 1):
                    url = response.url.split('=')[0] + '=' + str(page);
                    #print ('url: ' + url);
                    request = response.follow(url, callback = self.parse_get_news_title, dont_filter = True);
                    yield request;


    def parse_get_news_title(self, response):
        #print('parse_get_news_details -------> ' + response.url);
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

        #date = newsinfo.split(" ")[0].split("：")[-1] + " " + newsinfo.split(" ")[1];
        #source = newsinfo.split(" ")[2].split("：")[-1];

        searchObj = re.search( r'(\d\d\d\d-.*-.*:.*:\d\d).*', newsinfo, re.M);
        if (searchObj):
            date = searchObj.group(1);
        else:
        	date = "";

        searchObj = re.search( r'(来源：.*)', newsinfo, re.M);
        if (searchObj):
            source = searchObj.group(1)[4:];
        else:
        	source = "";

        
        content_text = "";
        contents = div_selectors.xpath('.//div[@id="newscontent"]').xpath("string()").extract_first();   #正文
        #print(contents);
        content_text = contents.split('分享到')[0].replace('\r\n\r\n', '\r\n');

        
        """
        content_text = response.xpath("//div[@id='newscontent']").extract()[0];
        print(content_text);
        pattern = re.compile(r'(<div .*>)|(</div>)|(<p .*>)|(</p>)|(<a .*>)|(</a>)|(<span .*/span>)|(<script .*>)|(document.*\r\n)|(</script>)');
        print('pattern.findall: ', pattern.findall(content_text));
        out = re.sub(pattern, "", content_text);
        out = out.replace("\r\n\r\n\r\n", "\r\n");
        out = out.replace("\r\n\r\n", "\r\n");
        print('out: ', out);
        """

        #content_text = div_selectors.xpath('.//div[@id="newscontent"]').xpath("string()").extract();   #正文取所有段落
        #print (content_text)


        '''
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
        '''

        content_text = content_text.replace("\r\n\r\n", "\r\n");

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
        
        #查找图片链接，下载, 并上传
        img_selectors = div_selectors.xpath('.//img[@src]');
        item['pic_url'] = "";
        img_count = 0;
        for img_selector in img_selectors:
            width = img_selector.xpath("@width").extract_first();  #过滤掉不显示的图片
            if (width == "0"):
                continue;
            img_src = img_selector.xpath("@src").extract_first();
            img_count += 1;
            if (img_src[0:4] != "http"):                           #有些图片的url需要补齐
                img_src = 'http://www.foodscn.cn' + img_src;
                
            #print("img_count:" + str(img_count) + " " + img_src);

            #下载图片并上传
            #request = response.follow(url = img_src, callback = self.parse_image);
            #request.meta['title'] = title;
            item['pic_url'] += img_src + ";";
            #yield request;

        item['pic_num'] = img_count;
        yield item;
        self.newsCount = self.newsCount + 1;
        print ("[%s] count %d" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.newsCount));
        #print(item, "\r\n");


        #下载图片并上传
    def parse_image(self, response):
        filename = "./pic/" + response.url.split("/")[-1];
        with open(filename, 'wb') as f:
            f.write(response.body);

        self.picsCount += 1;

        print ("[%s] pictureCount %d" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), self.picsCount));

        transport = paramiko.Transport(('106.12.******', 22))
        transport.connect(username='root', password='******')
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(item['fileName'], '/root/food_safety/pictures/' + item['fileName'].split('/')[-1]);
        transport.close();
        os.remove(item['fileName']);  #删除本地文件

