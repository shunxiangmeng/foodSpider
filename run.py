# -*- coding: utf-8 -*-

import time
import os


if __name__ == '__main__':
	while True:
		os.system("scrapy crawl foodscn --nolog");
		time.sleep(60*60);

