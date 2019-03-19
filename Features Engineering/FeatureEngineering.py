import pandas as pd
import numpy as np


class FeatureExtract:

    def __init__(self, FilePath):
        self.FilePath = FilePath
        self.holiday = ['2017-01-01','2017-01-02','2017-01-27',
                      '2017-01-28','2017-01-29','2017-01-30',
                      '2017-01-31','2017-02-01','2017-02-02',
                      '2017-04-02','2017-04-03','2017-04-04',
                      '2017-04-29','2017-04-30','2017-05-01',
                      '2017-05-28','2017-05-29','2017-05-30',
                      '2017-10-01','2017-10-02','2017-10-03',
                      '2017-10-04','2017-10-05','2017-10-06',
                      '2017-10-07','2017-10-08','2018-01-01',
                      '2018-02-15','2018-02-16','2018-02-17',
                      '2018-02-18','2018-02-19','2018-02-20','2018-02-21']
        self.northesat = ['黑龙江省', '吉林省', '辽宁省']
        self.huaeast = ['上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '台湾省']
        self.huanorth = ['北京市', '天津市', '山西省', '河北省', '内蒙古自治区']
        self.huacenter = ['湖北省', '湖南省', '河南省']
        self.huasouth = ['广东省', '广西壮族自治区', '海南省', '香港特别行政区', '澳门特别行政区']
        self.southwest = ['四川省', '贵州省', '云南省', '重庆市', '西藏自治区']
        self.northwest = ['陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区']

    def readFile(self):
        data = pd.read_csv(self.FilePath)
        if '运价（元/吨）' in data.columns.tolist():
            data.drop(['Unnamed: 0','start_weather','desti_max_temp','desti_min_temp','desti_weather','详细品类','起运地经度','起运地纬度',
            '目的地经度','目的地纬度','start_formatted_address','start_district','start_city','start_township','desti_formatted_address',
            'desti_district','desti_city','desti_township','district_x','city_x','province_x','start_url','start_wind_direct','start_wind_scale',
            'district_y','city_y','province_y','desti_url','desti_wind_direct','desti_wind_scale'],axis=1,inplace=True)
            data = data[data['运价（元/吨）'] < 750]
            data.reset_index(inplace=True)
            data.drop('index',axis=1,inplace=True)
        if '运价（元/吨）' not in data.columns.tolist():
            data.drop(['Unnamed: 0','钢材品类','起运地经度','起运地纬度','目的地经度','目的地纬度','start_district','start_city','desti_district','desti_city',
               'start_weather_url','start_weather','start_wind_dire','start_wind_scale','desti_weather_url','desti_max_temp','desti_min_temp',
               'desti_weather','desti_wind_dire','desti_wind_scale','desti_unit_oil_price'],axis=1,inplace=True)    
        return data

    def date_transform(self, date):
        if date in self.holiday:
            x = 1
        else:
            x = 0
        return x

    def holidayTranseform(self,data):
        date = data[['日期']].applymap(self.date_transform)
        date.rename(columns={'日期': '节日'}, inplace=True)
        data = data.join(date)
        return data

    def season_transform(self, date):
        if date[5:7] == '01' or date[5:7] == '02' or date[5:7] == '03':
            x = 1
        elif date[5:7] == '04' or date[5:7] == '05' or date[5:7] == '06':
            x = 2
        elif date[5:7] == '07' or date[5:7] == '08' or date[5:7] == '09':
            x = 3
        elif date[5:7] == '10' or date[5:7] == '11' or date[5:7] == '12':
            x = 4
        else:
            x = 0
        return x

    def seasonTransform(self,data):
        date = data[['日期']].applymap(self.season_transform)
        date.rename(columns={'日期': '季节'}, inplace=True)
        data = data.join(date)
        date_dummies = pd.get_dummies(data['季节'])
        date_dummies.rename(columns={1: '春', 2: '夏', 3: '秋', 4: '冬'}, inplace=True)
        data = data.join(date_dummies)
        data.drop(['季节','日期'], axis=1, inplace=True)
        return data

    def province_transform(self, province):
        if province in self.northesat:
            x = 1
        elif province in self.huaeast:
            x = 2
        elif province in self.huanorth:
            x = 3
        elif province in self.huacenter:
            x = 4
        elif province in self.huasouth:
            x = 5
        elif province in self.southwest:
            x = 6
        elif province in self.northwest:
            x = 7
        else:
            x = 0
        return x

    def provinceTransform(self, data):
        if '运价（元/吨）' in data:
            data.loc[data['desti_province'] == '[]','desti_province'] = '天津市'
        start_district = data[['start_province']].applymap(self.province_transform)
        start_district.rename(columns={'start_province':'start_district'},inplace=True)
        data = data.join(start_district)
        desti_district = data[['desti_province']].applymap(self.province_transform)
        desti_district.rename(columns={'desti_province':'desti_district'},inplace=True)
        data = data.join(desti_district)
        start_district_dummies = pd.get_dummies(data['start_district'],prefix='start_district_')
        desti_district_dummies = pd.get_dummies(data['desti_district'],prefix='desti_district_')
        data = pd.concat([data,start_district_dummies,desti_district_dummies],axis=1)
        data.drop(['start_province','desti_province','start_district','desti_district'],axis=1,inplace=True)
        return data


    def getDummies(self,data):
        data = data.join(pd.get_dummies(data['车型'],prefix='车型_'))
        data = data.join(pd.get_dummies(data['一级品类']))
        data.rename(columns={1: '品类1', 2: '品类2', 3: '品类3', 4: '品类4'}, inplace=True)
        data.drop(['车型','一级品类'], axis=1, inplace=True)
        return data

    def mean_temp(self,data):
        data['start_max_temp'] = data['start_max_temp'].astype(np.float,inplace=True)
        data['start_min_temp'] = data['start_min_temp'].astype(np.float,inplace=True)
        mean_temp = []
        for i in range(len(data)):
            temp = (data['start_max_temp'][i] + data['start_min_temp'][i]) / 2
            mean_temp.append(temp)
        mean_t = pd.DataFrame(mean_temp)
        mean_t.rename(columns={0:'平均温度'},inplace=True)
        data = data.join(mean_t)
        data.drop(['start_max_temp','start_min_temp'],axis=1,inplace=True)
        return data
 
    def standard(self,data):
        std_oil_value = data[['oil_value']].apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        std_oil_value.rename(columns={'oil_value':'标准化油价'},inplace=True)
        data = data.join(std_oil_value)
        std_value = data[['货值（吨/元）']].apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        std_value.rename(columns={'货值（吨/元）':'标准化货值（吨/元）'},inplace=True)
        data = data.join(std_value)
        std_dist = data[['运距']].apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        std_dist.rename(columns={'运距':'标准化运距'},inplace=True)
        data = data.join(std_dist)
        std_car_size = data[['车长']].apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        std_car_size.rename(columns={'车长':'标准化车长'},inplace=True)
        data = data.join(std_car_size)
        std_temp = data[['平均温度']].apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        std_temp.rename(columns={'平均温度':'标准化平均温度'},inplace=True)
        data = data.join(std_temp)
        data.drop(['oil_value','货值（吨/元）','运距','车长','平均温度'],axis=1,inplace=True)
        if '运价（元/吨）' in data:
            data['运价（元/吨）'] = np.sqrt(data['运价（元/吨）'] + 0.4176)
        return data
    
    def fill_data(self,data):
        im_list = [0] * len(data)
        im_df = pd.DataFrame({'车型__8':im_list,'车型__9':im_list,'车型__10':im_list,
                              '车型__14':im_list,'车型__16':im_list,'车型__17':im_list,
                              '夏':im_list,'秋':im_list,'冬':im_list})
        data = pd.concat([data,im_df],axis=1)
        data = data[['订单类型', '交易类型', '节日', '春', '夏', '秋', '冬',
       'start_district__1', 'start_district__2', 'start_district__3',
       'start_district__4', 'start_district__5', 'start_district__6',
       'start_district__7', 'desti_district__1', 'desti_district__2',
       'desti_district__3', 'desti_district__4', 'desti_district__5',
       'desti_district__6', 'desti_district__7', '车型__0', '车型__2',
       '车型__3', '车型__4', '车型__5', '车型__6', '车型__7', '车型__8', '车型__9',
       '车型__10', '车型__11', '车型__12', '车型__13', '车型__14', '车型__15',
       '车型__16', '车型__17', '车型__19', '品类1', '品类2', '品类3', '品类4',
       '标准化油价', '标准化货值（吨/元）', '标准化运距', '标准化车长', '标准化平均温度']]
        return data


    def excute(self):
        data = self.readFile()
        data = self.holidayTranseform(data)
        data = self.seasonTransform(data)
        data = self.provinceTransform(data)
        data = self.getDummies(data)
        data = self.mean_temp(data)
        data = self.standard(data)
        if '运价（元/吨）' not in data:
            data = self.fill_data(data)
		data.drop(['春','夏','秋','冬'],axis=1,inplace=True)
        return data