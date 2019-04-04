# -*- coding:utf-8 -*-
import pymysql
import json

HOST_IP = '106.12.74.85'
HPST_PORT = 3306

class UPLOAD(object):

    def __init__(self, name):
    	self.name = name;


    def upload(self, data):
    	print("upload: %s" %data);

		


#test
up = UPLOAD('test');

#up.upload("123");

try:
	conn = pymysql.connect(host=HOST_IP, port=HPST_PORT, user='spider', passwd='spider', db='spider');
	cursor = conn.cursor()    #获取cursor游标
	sql = 'select * from food_safety_type;'
	cursor.execute(sql);
	ret = cursor.fetchall();
	cursor.close();
	conn.close();    #断开连接
	#print ret;
except pymysql.Error as e:
	conn.rollback();
	pass;