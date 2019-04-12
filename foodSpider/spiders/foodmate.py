# -*- coding: utf-8 -*-

import scrapy
import re
import os,time,sys
#from upload import *
from ..items import *
import json

filePath = './PDF/'
serverFilePath = "/root/food_safety/foodmate/pdf/"

#up = UPLOAD('sql');
g_found_standard_count = 0;

g_standardInfo = {};
g_standardInfo['xxyx'] = 0;
g_standardInfo['jjfz'] = 0;
g_standardInfo['jjss'] = 0;
g_standardInfo['yjfz'] = 0;
g_standardInfo['wz'] = 0;
g_standardInfo['sum'] = 0;
g_standardInfo['down'] = 0;

class FoodSpider(scrapy.Spider):
    name = "foodmate"

    def start_requests(self):
        urls = [
            'http://down.foodmate.net/standard/index.html',
        ]

        print ("Start Time: ", time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())));
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("....查找【国内标准】和【国外标准】... " + response.url);
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
            pass;
            #list = [];
            #list = [u"CAC标准", u"AOAC标准"];
            list = [u"CAC标准", u"AOAC标准", u"EU/EC欧盟指令条例", u"UNECE标准", u"澳新标准", u"FCC标准", u"JECFA标准", u"其它国外标准"];

        a_selectors = response.xpath("//a[@href]");
        for selector in a_selectors:
            text = selector.xpath("text()").extract_first();
            link = selector.xpath("@href").extract_first();
            for standard in list:
                if (text == standard):
                    #print(text);
                    #print(u'链接:' + link);

                    info = {}                           #创建信息参数
                    info['major'] = info_p['major'];    #大类
                    info['subclass'] = standard;        #小类
                    request = response.follow(link, callback=self.parse_standard_subclass_page);
                    request.meta['info']=info;    #传递参数
                    yield request;


    #在小类标准中翻页
    def parse_standard_subclass_page(self, response):
        global g_standardInfo;
        info_p = response.meta['info'];
        a_selectors = response.xpath('//cite');
        t = a_selectors.xpath('string()').extract_first();
        item_num = int(re.sub('\D', '', t.split('/')[0]));  #获取总条数
        page_num = int(re.sub('\D', '', t.split('/')[1]));  #获取总页数
        g_standardInfo['sum'] = g_standardInfo['sum'] + item_num;

        print (info_p['subclass'],'  ', t, '标准总条数:', g_standardInfo['sum']);
        #print (item_num, page_num);
        for i in range(1, page_num + 1):
            page_index = response.url + 'index-' + str(i) + '.html';
            #print page_index;
            info = {}                              #创建信息参数
            info['major'] = info_p['major'];       #大类
            info['subclass'] = info_p['subclass']; #小类
            request = response.follow(page_index, callback=self.parse_standard_subclass);
            request.meta['info']=info; 
            yield request;


    #查找小小类
    def parse_standard_subclass(self, response):
        global g_standardInfo;
        info_p = response.meta['info'];
        #print json.dumps(info_p);
        #print("--------[%s]->[%s]  " %(info_p['major'],info_p['subclass'])+ response.url);
        a_selectors = response.xpath('//div[@class="bz_list"]/ul/li');
        count = 0;
        for selector in a_selectors:
            a = selector.xpath("./div/ul/a");
            #print a
            link = a.xpath('@href').extract_first();
            if (a.xpath('./img[contains(@src, "yjfz.gif")]').extract_first() != None):  #已经废止的标准，不查询
                g_standardInfo['yjfz'] = g_standardInfo['yjfz'] + 1;
                continue;

            #print('---find count: %d------' %(count));
            count = count + 1;
            head = a.xpath("string()").extract_first();
            head = head.replace("\r\n", "");  #去掉换行符
            #print head
            #span = selector.xpath('./div/ul/span[@class="lb_ft"]');
            #text0 = span.xpath("string()").extract_first();
            #span = selector.xpath('./div/ul/span[@class="lb_bt"]');
            #text1 = span.xpath("string()").extract_first();
            #span = selector.xpath('./div/ul/span[@class="lb_bq"]');
            #text2 = span.xpath("string()").extract_first();
            #print(text0 + ' ' + text1 + ' ' + text2 + '\r\n');

            info = {};
            info['major'] = info_p['major'];
            info['subclass'] = info_p['subclass'];             #小类
            if (a.xpath('./img[contains(@src, "xxyx.gif")]').extract_first() != None):  #现行有效的标准
                info['status'] = u'现行有效';
                g_standardInfo['xxyx'] = g_standardInfo['xxyx'] + 1;
            elif (a.xpath('./img[contains(@src, "jjfz.gif")]').extract_first() != None):  #即将废止的标准
                info['status'] = u'即将废止';
                g_standardInfo['jjfz'] = g_standardInfo['jjfz'] + 1;
            elif (a.xpath('./img[contains(@src, "jjss.gif")]').extract_first() != None):  #即将实施的标准
                info['status'] = u'即将实施';
                g_standardInfo['jjss'] = g_standardInfo['jjss'] + 1;
            else:
                info['status'] = u'未知';
                g_standardInfo['wz'] = g_standardInfo['wz'] + 1;

            info['id'] = count;
            info['head'] = head;
            request = response.follow(link, callback=self.parse_standard_donwload_page);
            request.meta['info']=info;    #传递参数
            yield request;

    #PDF下载页
    def parse_standard_donwload_page(self, response):
        global g_found_standard_count, g_standardInfo;
        info_p = response.meta['info'];
        #print json.dumps(info_p);
        #print('--------[%s]->[%s]->[%s]  ' %(info_p['major'], info_p['subclass'], info_p['head']));

        info = {};
        info['major'] = info_p['major'];       #大类
        info['subclass'] = info_p['subclass']; #小类
        info['head'] = info_p['head'];
        info['status'] = info_p['status'];

        s_type_table = response.xpath('//table[@class="xztable" and @cellpadding="5"]');
        info['type'] = s_type_table.xpath('./tr[1]/td[1]/text()').extract_first();  #标准类别
        info['publish'] = s_type_table.xpath('./tr[1]/td[2]/text()').extract_first();  
        info['implement'] = s_type_table.xpath('./tr[2]/td[2]/text()').extract_first();  
        info['department'] = s_type_table.xpath('./tr[3]/td[1]/text()').extract_first();  
        info['abolish'] = s_type_table.xpath('./tr[3]/td[2]/text()').extract_first();  

        #print info['type'];
        #print 'status:  ',info['status'];
        #print '发布日期：',info['publish'];
        #print '实施日期：',info['implement'] ;
        #print '颁发部门：',info['department'];
        #print '废止日期：',info['abolish'];

        describe = response.xpath('//div[@class="bznr_box"]');
        #print describe
        text = describe.xpath('string()').extract_first().replace("\r\n\r\n", "\r\n");
        info['describe'] = text;
        downLink = response.xpath('//a[@class="telecom" and @href]');
        downLink = downLink.xpath('@href').extract_first();
        info['download_url'] = 'null';
        if (downLink != None):
            info['download_url'] = downLink;
            g_standardInfo['down'] = g_standardInfo['down'] + 1;

            #request = response.follow(downLink, callback=self.parse_standard_donwload);
            #request.meta['info']=info;    #传递参数
            #yield request;
        g_found_standard_count = g_found_standard_count + 1;
        if (g_found_standard_count % 100 == 0):
            print ('[',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),']','found_count:', g_found_standard_count, 'can_down:', g_standardInfo['down'],'现行有效:',g_standardInfo['xxyx'],\
            '即将废止:',g_standardInfo['jjfz'],'即将实施:',g_standardInfo['jjss'],'未知:',g_standardInfo['wz'],'已经废止:',g_standardInfo['yjfz'],'SUM:', \
            g_standardInfo['xxyx']+g_standardInfo['jjfz']+g_standardInfo['jjss']+g_standardInfo['wz']+g_standardInfo['yjfz']);


    def parse_standard_donwload(self, response):
        global g_found_standard_count;
        info = response.meta['info'];
        #print json.dumps(info);
        #filename = filePath + response.url.split('/')[-1];
        filename = filePath + info['head'].replace('/', '') + '.pdf';
        with open(filename, 'wb') as f:
            pass;
            f.write(response.body);
        info['fileName'] = filename;
        info['serverFileName'] = serverFilePath + info['head'].replace('/', '') + '.pdf';
        #print 'download: ' + info['major'] + '->' + info['subclass'] + '->' + info['head'] + ' to '+ filename;
        #print(response.url + "\r\n")


        #上传数据 todo
        #up.upload(info);  








