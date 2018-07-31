# -*- coding=utf8 -*-
# author:jiyuan

import numpy as np
import pandas as pd  # 数据框
import time
import datetime    # 时间
import os
import traceback

from auto_home.tools import tools as tls
from tool_common import tool_common as tlc


def get_car_config_info(car_sort):
    #start_urls = ['http://www.autohome.com.cn/grade/carhtml/%s.html' % chr(ord('A') + i) for i in range(26)]
    url_pattern = 'http://www.autohome.com.cn/grade/carhtml/{}.html'
    url_config_pattern = 'https://car.autohome.com.cn/config/series/{}.html'

    # 读取是否已经获取过数据，并且是否有配置数据
    try:
        car_info_saved=pd.read_csv('auto_home/car_file/car_info_log.csv')
    except:
        car_info_saved=pd.DataFrame(columns=['car','config'])

    count=0
    for sort in car_sort:
        url= url_pattern.format(sort)
        car_ids, car_names = tls.get_car_ids(url)
        if car_ids:
            for n,car_id in enumerate(car_ids):
                car_list=car_info_saved['car'].tolist()
                car_id=tlc.str_convert(car_id[1:])
                car_brand = tlc.str_convert(car_names[n])
                car_name_id=tlc.str_convert(car_brand+'_'+car_id)
                if car_name_id in car_list:
                    print 'already get {}'.format(car_name_id)
                else:
                    url_config = url_config_pattern.format(car_id)
                    tlc.sleep_time_random()
                    try:
                        df=tls.get_car_config_table(url_config)
                    except:
                        err=traceback.format_exc()
                        tlc.log_err(err)
                    if df.empty:
                        print 'no config data {0}@{1}'.format(car_name_id,datetime.datetime.now())
                        car_info_saved=car_info_saved.append([{'car':car_name_id,'config':0}])
                        car_info_saved.to_csv('auto_home/car_file/car_info_log.csv', index=False)
                    else:
                        df.to_excel('auto_home/car_file/{}.xls'.format(car_name_id).decode('utf8'),index=False)
                        car_info_saved=car_info_saved.append([{'car':car_name_id,'config':1}])
                        car_info_saved.to_csv('auto_home/car_file/car_info_log.csv', index=False)
                        count=count+1
                        print 'get {0}@{1}'.format(car_name_id,datetime.datetime.now())
    #car_info_saved.to_csv('auto_home/car_file/car_info_log.csv',index=False)
    return count




