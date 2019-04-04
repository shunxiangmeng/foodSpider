# -*- coding: utf-8 -*-

import scrapy
import re
import os
from upload import *
from ..items import *
import json

filePath = './PDF/'

up = UPLOAD('sql');

class FoodSpider(scrapy.Spider):
    name = "foodmate"

    def start_requests(self):
        urls = [
            'http://down.foodmate.net/standard/index.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("...............查找【国内标准】和【国外标准】... " + response.url);
        # 获取所有<a>标签
        a_selectors = response.xpath("//a[@title and @href]");
        # 对每个标签进行循环操作
        for selector in a_selectors:
            # 解析出链接的文本
            text = selector.xpath("text()").extract_first()
            #print(text);
            # 解析出链接的网址
            link = selector.xpath("@href").extract_first();
            if ((text == u"国内标准") or (text == u"国外标准")):
                #print('depth1: ' + text);
                #print('url: ' + link +'\n');

                info = {}                #创建信息参数
                info['major'] = text;    #大类
                #print json.dumps(info)
                request = response.follow(link, callback=self.parse_standard_major);
                request.meta['info']=info;    #传递参数
                yield request;

    #查找小类标准
    def parse_standard_major(self, response):
        info_p = response.meta['info'];
        #print json.dumps(info_p);
        print("---------major[%s]---------------------------------------  " %(info_p['major']) + response.url);
        if (info_p['major'] == u'国内标准'):
            #list = [u"国家标准"];
            list = [u"国家标准", u"进出口行业标准", u"农业标准", u"水产标准", u"商业标准", u"轻工标准", u"地方标准", u"卫生标准", u"化工标准", u"医药标准", u"烟草标准", u"认证认可标准", u"食品安全企业标准", u"其它国内标准", u"团体标准"];
        elif (info_p['major'] == u"国外标准"):
            #list = [u"CAC标准", u"AOAC标准"];
            list = [u"CAC标准", u"AOAC标准", u"EU/EC欧盟指令条例", u"UNECE标准", u"澳新标准", u"FCC标准", u"JECFA标准", u"其它国外标准"];

        a_selectors = response.xpath("//a[@href]");
        for selector in a_selectors:
            text = selector.xpath("text()").extract_first();
            link = selector.xpath("@href").extract_first();
            for standard in list:
                if (text == standard):
                    print(text);
                    print(u'链接:' + link);

                    info = {}                           #创建信息参数
                    info['major'] = info_p['major'];    #大类
                    info['subclass'] = standard;        #小类
                    request = response.follow(link, callback=self.parse_standard_subclass);
                    request.meta['info']=info;    #传递参数
                    yield request;


    #查找小小类
    def parse_standard_subclass(self, response):
        info_p = response.meta['info'];
        #print json.dumps(info_p);
        print("--------------major[%s] subclass[%s]-------------------------  " %(info_p['major'],info_p['subclass'])+ response.url);
        a_selectors = response.xpath('//div[@class="bz_list"]/ul/li');
        count = 0;
        for selector in a_selectors:
            a = selector.xpath("./div/ul/a");
            #print a
            link = a.xpath('@href').extract_first();
            img = a.xpath('./img[contains(@src, "xxyx.gif")]').extract_first();   #只查现行有效的标准
            if (img != None):
                print('---find count: %d------' %(count));
                count = count + 1;
                #print(u'现行有效')
                head = a.xpath("string()").extract_first();
                head = head.replace("\r\n", "");  #去掉换行符
                print head
                span = selector.xpath('./div/ul/span[@class="lb_ft"]');
                text0 = span.xpath("string()").extract_first();
                span = selector.xpath('./div/ul/span[@class="lb_bt"]');
                text1 = span.xpath("string()").extract_first();
                span = selector.xpath('./div/ul/span[@class="lb_bq"]');
                text2 = span.xpath("string()").extract_first();
                print(text0 + ' ' + text1 + ' ' + text2 + '\r\n');

                info = {};
                info['major'] = info_p['major'];
                info['subclass'] = info_p['subclass'];        #小类
                info['id'] = count;
                info['head'] = head;
                request = response.follow(link, callback=self.parse_standard_donwload_page);
                request.meta['info']=info;    #传递参数
                yield request;

    #PDF下载页
    def parse_standard_donwload_page(self, response):
        info_p = response.meta['info'];
        #print json.dumps(info_p);
        print('--------major[%s] subclass[%s] head[%s]------' %(info_p['major'], info_p['subclass'], info_p['head']));
        a_selectors = response.xpath('//div[@class="title2"]');
        for selector in a_selectors:
            span = selector.xpath('./span');
            text = span.xpath("string()").extract_first();
            #print(text)
            describe = selector.xpath('//div[@class="bznr_box"]');
    		#print(describe)
            text = describe.xpath('string()').extract_first();
            print(text);
            downLink = response.xpath('//a[@class="telecom" and @href]')
            downLink = downLink.xpath('@href').extract_first();
            #print('PDF file download link:  %s' %downLink);
            if (downLink != None):
                pass;
                request = response.follow(downLink, callback=self.parse_standard_donwload);
                request.meta['info']=info_p;    #传递参数
                yield request;

    def parse_standard_donwload(self, response):
        info = response.meta['info'];
        #print json.dumps(info);
        filename = filePath + response.url.split('/')[-1];
        filename = filePath + info['head'].split('/')[-1] + '.pdf';
        with open(filename, 'wb') as f:
            pass;
            f.write(response.body);
        info['fileName'] = filename;
        print 'download: ' + info['major'] + '->' + info['subclass'] + '->' + info['head'] + ' to '+ filename;
        print(response.url + "\r\n")
        
        #上传数据 todo
        #up.upload(info);  








