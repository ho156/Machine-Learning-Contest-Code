# project：GetWeather
# create at 2018/7/8
# author：史志通


from urllib import request
from bs4 import BeautifulSoup as bs
import logging  # 引入logging模块
import os.path
import time
import pandas as pd
import re



# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y%m%d', time.localtime(time.time()))
log_path = os.path.dirname(os.getcwd()) + '/Logs/'
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

class GetWeather:
    def __init__(self):
        self.base_url = "https://lishi.tianqi.com/"
        self.html = request.urlopen(self.base_url)
        self.soup = bs(self.html, "html5lib")

    def remove_blank(self,s):
        if isinstance(s, str):
            if s.strip() == "":
                pass
            else:
                return s.strip()
        else:
            logger.debug("not str:", s)
            return None

    def get_weather_temp(self, dates, base_url):

        res = []
        dates_list = dates.split("-")
        year_mon = "".join(dates_list[:2])
        url = base_url.replace("index", year_mon)
        res.append(url)
        try:
            html = request.urlopen(url)
        except:
            html = None
        if html:
            soup = bs(html, "html5lib")
            a_tag = soup.find("a", text=dates)
            if a_tag:

                ul = a_tag.parent.next_siblings
            else:
                ul = None
                logger.debug("find no a tag:%s" % url)

            if ul:
                for i in ul:
                    sub_res = self.remove_blank(i.string)
                    if sub_res:
                        res.append(sub_res)
                return res
        else:
            logger.debug("获取网页失败:%s" % url)
            return None


    def get_url(self, loc):
        soup = self.soup
        # print(soup)
        if loc:
            try:
                target = soup.find("a", text=re.compile("^" + loc + "w*"))
            except:
                target = None
                print(loc)
            if target:
                return target.attrs["href"]
            else:
                return None
        else:
            return None

    # target = soup.find("a", text = re.compile("^"+"河西"+"w*"))
    # print(target)
    def get_weather(self, values):
        dates, district, city, province =values[0], values[1], values[2], values[3]
        if district !="[]":
            if len(district)>=2:
                district = district[:-1]
                base_url = self.get_url(district)
            else:
                base_url = self.get_url(district)
        else:
            base_url = None
        if not base_url:
            if city !="[]":
                if len(city)>=2:
                    city = city[:-1]
                    base_url = self.get_url(city)
                else:
                    base_url = self.get_url(city)
            else:
                if len(province)>=2:
                    base_url = self.get_url(province)
                else:
                    base_url = self.get_url(province)

        if base_url:
            res = self.get_weather_temp(dates, base_url)
            if res:
                values = list(values)
                values.extend(res)
                return values
if __name__=="__main__":
    pre_data = pd.read_excel("detail_loc.xlsx")
    pre_data_values = pre_data.values
    count = 0
    f = open("wether_info.txt", "a", encoding="utf-8")
    for i in pre_data_values[73040:]:
        obj = GetWeather()
        sub_res = obj.get_weather(i)
        f.writelines(str(sub_res)+'\n')
        count += 1
        print(count)
    f.close()

