# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import datetime
from twisted.enterprise import adbapi
import paramiko

class FoodspiderPipeline(object):

    def process_item(self, item, spider):
        return item;




class FoodCfsnPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool;

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值

    	adbparams = dict(
    		host = settings['MYSQL_HOST'],
    		db   = settings['MYSQL_DBNAME'],
    		user = settings['MYSQL_USER'],
    		password = settings['MYSQL_PASSWORD'],
    		cursorclass = pymysql.cursors.DictCursor
    	);

    	# 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
    	dbpool = adbapi.ConnectionPool('pymysql', **adbparams);
    	# 返回实例化参数
    	return cls(dbpool);

    def process_item(self, item, spider):
    	#print ('spider.name: ', spider.name);
    	# 使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
    	if (spider.name == "foodcfsn"):
    		query = self.dbpool.runInteraction(self.do_insert_cfsn, item);
    	elif (spider.name == "foodscn"):
    		query = self.dbpool.runInteraction(self.do_insert_scn, item);
    	elif (spider.name == "foodmate"):
    		query = self.dbpool.runInteraction(self.do_insert_mate, item);

    	# 添加异常处理
    	query.addCallback(self.handle_error);

    #
    def do_insert_cfsn(self, cursor, item):
    	# 对数据库进行插入操作，并不需要commit，twisted会自动commit
    	ndt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");  #当前时间
    	try:
    		insert_sql = """
    		insert into food_safety_cfsn(major, title, status, publish_time, update_time, source, content_len, content, url, pic_num, pic_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    				"""
    		cursor.execute(insert_sql, (item['major'], (item['title']), "新增", item['publish'], ndt, item['source'], item['content_len'], (item['content']), item['url'],item['pic_num'], item['pic_url']));
    	except pymysql.Error as e:
    		#print ("except", e);
    		if (e.args[0] == 1062):   #已有数据，则更新
    			update_sql = "update food_safety_cfsn set source='%s', content_len='%d', major='%s', publish_time='%s', update_time='%s', status='更新', content='%s', url='%s',pic_num='%s', pic_url='%s'\
    			where title='%s'" %(item['source'], item['content_len'], item['major'], item['publish'], ndt, item['content'], item['url'], item['pic_num'],item['pic_url'], (item['title']));
    			#print(update_sql);
    			try:
    				cursor.execute(update_sql);
    			except pymysql.Error as e:
    				print ("execute error: " + item['title'] + " " + item['url']);
    				#print(update_sql);
    		else:
    			print ("execute error: " + e + item['title'] + " " + item['url']);
    	#return 0;


    #中国安全食品网 数据表插入
    def do_insert_scn(self, cursor, item):
    	ndt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");  #当前时间
    	try:
    		insert_sql = """
    		insert into food_safety_scn(major, title, status, publish_time, update_time, source, content_len, content, url, pic_num, pic_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    				"""
    		cursor.execute(insert_sql, (item['major'], (item['title']), "新增", item['publish'], ndt, item['source'], item['content_len'], (item['content']), item['url'],item['pic_num'], item['pic_url']));
    	except pymysql.Error as e:
    		#print ("except", e);
    		if (e.args[0] == 1062):   #已有数据，则更新
    			update_sql = "update food_safety_scn set source='%s', content_len='%d', major='%s', publish_time='%s', update_time='%s', status='更新', url='%s',pic_num='%s', pic_url='%s'\
    			where title='%s'" %(item['source'], item['content_len'], item['major'], item['publish'], ndt, item['url'], item['pic_num'],item['pic_url'], (item['title']));
    			#print(update_sql);
    			cursor.execute(update_sql);
    	return 0;


    #
    def do_insert_mate(self, cursor, item):
    	ndt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");  #当前时间
    	try:
    		insert_sql = """
    		insert into food_safety_foodmate(standard_major, standard_type, name, get_status, status, publish_date, implement_date, abolish_date, department, pdf_file_name, pdf_download_url, url, update_time) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    				"""
    		cursor.execute(insert_sql, (item['major'],item['standard_type'],item['title'], "新增", item['standard_status'], item['publish'], item['implement'],item['abolish'], item['department'],item['fileName'],item['download_url'],item['url'],ndt));
    	except pymysql.Error as e:
    		#print ("except", e);
    		if (e.args[0] == 1062):   #已有数据，则更新
    			update_sql = "update food_safety_foodmate set get_status='更新', status='%s', publish_date='%s', implement_date='%s', abolish_date='%s', update_time='%s'\
    			where name='%s'" %(item['standard_status'],item['publish'], item['implement'], item['abolish'], ndt, item['title']);
    			#print(update_sql);
    			cursor.execute(update_sql);



    def handle_error(self, failure):
    	if failure:
    		# 打印错误信息
    		print("handle_error............");
    		print(failure);




