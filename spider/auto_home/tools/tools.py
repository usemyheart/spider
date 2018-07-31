# -*- coding=utf8 -*-
# author:jiyuan
import numpy as np
import pandas as pd  # 数据框

import re
import HTMLParser
from scrapy import Selector
from selenium import webdriver

import datetime


from tool_common import tool_common as tlc

#================================================
path='../car_file/'

#=======================================================#
# 汽车之家品牌页面根据获取车型id,得到配置页面的网址
# url='http://www.autohome.com.cn/grade/carhtml/A.html'
def get_car_ids(url):
    xml = tlc.getHtml(url, type='xml')
    car_ids=xml.xpath('.//li/@id')  # 列表
    names = xml.xpath('.//li//h4//a/text()')
    return car_ids,names


# 汽车之家配置页面table数据提取
# 难点css中插入字符，需要js解析
#url = 'https://car.autohome.com.cn/config/series/3170.html'
def get_car_config_table(url):
    # 提取页面，并解码css
    # 提取目标脚本
    pattern_script = re.compile(r"""
        <script>
        (                           #(): all js code
            \(function.*?
            '\.hs_kw'.*?'(.*?)'     #(.*?): postfix _baikeYK in '.hs_kw' + $index$ + '_baikeYK'
            .*?
        )
        </script>
    """, re.X)  # |re.S

    # 改造目标脚本
    # 中间插入 push 语句
    # myarr.push([$index$, $temp$]);
    # $InsertRule$($index$, $temp$);
    pattern_code = re.compile(r"""
        ^\(function\((.*?)\)  # (.*?): function argument
        \{
            (.*?)             # (.*?): top half js code inside {}
            (\$InsertRule\$\(\$index\$,\s*\$temp\$\);)    #(...)
            (.*?)             # (.*?): bottom half js code inside {}
        \}             
        \)\(document\);$      # discard
    """, re.X)

    repl_code = r"""
    return myfunc(document);
    function myfunc(\1){
        myarr = Array();
        \2
        myarr.push([$index$, $temp$]);
        \3
        \4
        return myarr;
    }
    """

    # 根据返回字典填充 html
    myjs = """
    var arr = document.querySelectorAll('.hs_kw%(key)s%(postfix)s');

    if(arr.length !== 0){
        for (var i=0; i<arr.length; i++){
            console.log('.hs_kw%(key)s%(postfix)s %(value)s');
            arr[i].innerHTML = '%(value)s' + arr[i].innerHTML;
        }
    }

    return null;
    """
    # 可以不弹出浏览器，避免影响使用电脑
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    dr = webdriver.Chrome(chrome_options=chrome_options)
    dr.get(url)
    # dr.refresh()

    # 提取多个代码段<script>...</script>及其中的class name 后缀
    script_list = pattern_script.findall(dr.page_source)
    for (js, postfix) in script_list:
        # print(postfix)
        js = HTMLParser.HTMLParser().unescape(js)  # &amp;  &
        js = pattern_code.sub(repl_code, js)
        ret = dr.execute_script(js)
        mydict = dict(ret)
        # print(mydict)
        # 根据返回 myarr 字典填充文字到 html 对应 class name 的 span 内部
        for (key, value) in mydict.items():
            #print(postfix, key, value)
            js = myjs % ({'postfix': postfix.encode('utf8'), 'key': key, 'value': value.encode('utf8')})
            # print(js)
            dr.execute_script(js)

    sel = Selector(text=dr.page_source)
    # sel.css(‘span[class*="hs_kw"]‘).extract()

    # 数据解析并调整为表的格式
    df = pd.DataFrame()
    for n, t in enumerate(sel.css('table')):
        if n in [0, 2]:
            pass
        elif n == 1:  # 同一个车型不同型号解析
            i = -1
            for row in t.xpath('.//tr'):
                # print('-'*100)
                i = i + 1
                j = -1
                col_list = []
                for col in row.xpath('.//th|.//td'):
                    j = j + 1
                    r = ''.join(col.xpath('.//node()/text()').extract()[2:-3])
                    if r:
                        pass
                    else:
                        r = ''.join(col.xpath('.//node()/text()').extract())
                    col_list.append(r)
                    # print(i,j,r)
                df = df.append([col_list])
        else:
            i = -1
            for row in t.xpath('.//tr'):
                i = i + 1
                j = -1
                col_list = []
                for col in row.xpath('.//th|.//td'):
                    j = j + 1
                    r = ''.join(col.xpath('.//node()//text()').extract())
                    if r:
                        pass
                    else:
                        r = ','.join(col.xpath('.//li//a//@title|.//span//@title').extract())
                    col_list.append(r)
                    # print(i,j,r)
                df = df.append([col_list])

    dr.close()
    dr.quit()   # 关闭浏览器

    return df

# 保存没有配置数据的车型
def save_url(name,id):
    f = open(path + 'car_log.txt', 'a+')
    f.write(tlc.str_convert(name+'_'+id) + '@' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    f.close()

