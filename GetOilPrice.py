# project:GetOilPrice
# created at 2018/7/8
# author：史志通

base_url = "https://energy.cngold.org//list_427_all.html"
from urllib import request
from bs4 import BeautifulSoup as bs
import json
import re


class get_Oil_price:

    def __init__(self, base_url):
        self.base_Url = base_url

    #获取日期URL
    def get_list_url(self):
        html = request.urlopen(self.base_Url)
        soup = bs(html, "html5lib")
        yiqi_li = soup.find("div",text = "2017年柴油资讯列表").parent
        date_url_list = []
        if yiqi_li:
            date_list = yiqi_li.findAll("li")
            for i in date_list:
                a_tag = i.find("a")
                date_url_list.append((a_tag.text, a_tag.attrs["href"]))
            return date_url_list
        else:
            print("没有获取种子页")
            raise BaseException

    def get_list_page(self, date_url_tuple):
        date, date_url = date_url_tuple[0], date_url_tuple[1]
        html = request.urlopen(date_url)
        soup = bs(html)
        detail_li = soup.find("a", text = re.compile("\w+最新\w*柴油\w*价格\w+"))
        print(date, detail_li)
        if detail_li:
            detail_url = detail_li.attrs["href"]
            return (date, detail_url)
        else:
            pass

    def parse_detail_page(self, detail_url_tuple):
        date, detail_url = detail_url_tuple[0], detail_url_tuple[1]
        html = request.urlopen(detail_url)
        soup = bs(html)
        table = soup.find("table")
        tr_list = table.findAll("tr")
        district_list = []
        unit_price_list = []
        for i, element in enumerate(tr_list):
            if i==0:
                td_list = element.findAll("td")
                for j, tag in enumerate(td_list):
                    if j==0:
                        district = tag.text
                    elif j==1:
                        unit_price = tag.text
            else:
                td_list = element.findAll("td")
                for j, tag in enumerate(td_list):
                    if j==0:
                        district_list.append(tag.text)
                    elif j==1:
                        unit_price_list.append(tag.text)
        return (date,{district:district_list,unit_price:unit_price_list})

    def get_oil_info(self):
        date_url_list = self.get_list_url()
        res_dic = {}
        for i in date_url_list:
            detail_dict = self.get_list_page(i)
            if detail_dict:
                date, middle_res = self.parse_detail_page(detail_dict)
                res_dic[date] = middle_res
        res_js = json.loads(res_dic)
        return res_js

if __name__=="__main__":
    obj = get_Oil_price("https://energy.cngold.org//list_427_all.html")
    res_js = obj.get_oil_info()
    with open("oil_price.json","w", encoding="utf-8") as json_file:
        json.dumps(res_js,json_file,ensure_ascii=False)





