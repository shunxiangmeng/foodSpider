# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import datetime
from twisted.enterprise import adbapi


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

    	print ("ConnectionPool");
    	# 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
    	dbpool = adbapi.ConnectionPool('pymysql', **adbparams);
    	# 返回实例化参数
    	return cls(dbpool);

    def process_item(self,item,spider):
    	# 使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
    	query = self.dbpool.runInteraction(self.do_insert, item);
    	# 添加异常处理
    	query.addCallback(self.handle_error);

    def do_insert(self, cursor, item):
    	# 对数据库进行插入操作，并不需要commit，twisted会自动commit
    	ndt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S");  #当前时间
    	try:
    		insert_sql = """
    		insert into food_safety_foodcfsn(major, title, publish, update_time, source, content_len, content) VALUES(%s, %s, %s, %s, %s, %s, %s)
    				"""
    		cursor.execute(insert_sql, (item['major'], item['title'], item['publish'], ndt, item['source'], item['content_len'], item['content']));
    	except pymysql.Error as e:
    		#print ("except", e);
    		if (e.args[0] == 1062):   #已有数据，则更新
    			update_sql = "update food_safety_foodcfsn set source='%s', content='%s', content_len='%d', major='%s', publish='%s', update_time='%s'\
    			where title='%s'" %(item['source'], item['content'], item['content_len'], item['major'], item['publish'], ndt, item['title']);

    			#print(update_sql);
    			cursor.execute(update_sql);
    	#return item;

    def handle_error(self, failure):
    	if failure:
    		# 打印错误信息
    		print(failure);




