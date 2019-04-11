# -*- coding:utf-8 -*-
import pymysql
import json
import paramiko
import os

HOST_IP = '106.12.74.85'
HPST_PORT = 3306
USER = 'spider'
PASSWD = 'spider'
DATABASE = 'spider'

upload_count = 0;

class UPLOAD(object):

    def __init__(self, name):
    	self.name = name;

    def upload_test(self, data):
    	print("upload: %s" %data);
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

    def upload_file(self, file):#
    	transport = paramiko.Transport(('106.12.95.104', 22))
    	transport.connect(username='root', password='shian12345')
    	sftp = paramiko.SFTPClient.from_transport(transport)
    	sftp.put(file, '/root/food_safety/foodmate/pdf/' + file.split('/')[-1]);
    	transport.close();
    	os.remove(file);  #本地

    def upload(self, info):
    	global upload_count
    	#print info['serverFileName'];
    	#print (info);
    	try:
    		conn = pymysql.connect(host=HOST_IP, port=HPST_PORT, user=USER, passwd=PASSWD, db=DATABASE);
    		cursor = conn.cursor();    #获取cursor游标
    		#sql = "INSERT INFO food_safety_foodmate (standard_major) values(1, " + info['major'] + ");"
    		#sql = "update food_safety_foodmate set standard_major= '" + info['major'] + "' where ";
    		cursor.execute("INSERT INTO food_safety_foodmate(standard_major, standard_type, name, status, publish_date, implement_date, abolish_date, \
    			department, brief, pdf_file_name, pdf_download_url) \
    			values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", \
    			[info['major'], info['subclass'], info['head'], info['status'], info['publish'], info['implement'], info['abolish'], info['department'], \
    			info['describe'], info['serverFileName'], info['download_url']]);
    		#print sql
    		#cursor.execute(str(sql));
    		conn.commit();
    		cursor.close();
    		conn.close();    #断开连接
    		self.upload_file(info['fileName']);
    		upload_count = upload_count + 1;
    		print("upload_count : %d" %(upload_count))

    	except pymysql.Error as e:
    		print ("Error %d: %s" % (e.args[0], e.args[1]));
    		pass;

    def update(self, info):
    	pass;


#test
'''
up = UPLOAD('test');
info = {};
info['major'] = "text";
up.upload(info);
'''

