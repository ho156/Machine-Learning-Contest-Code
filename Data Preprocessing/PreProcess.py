
import pandas as pd

class PreProcessing:

    def __init__(self,FilePath,OilPath):
        self.FilePath = FilePath
        self.OilPath = OilPath

    def readFile(self):
        data = pd.read_csv(self.FilePath)
        oil = pd.read_csv(self.OilPath)
        oil.drop('Unnamed: 0',axis=1,inplace=True)
        return data,oil

    def fillNA(self,data):
        fill_val = data[data['一级品类'] == 1][data['订单类型'] == 0][data['交易类型'] == 1][data['车型'] == 0]
        data.loc[data['货值（吨/元）'].isnull(),'货值（吨/元）'] = fill_val['货值（吨/元）'].median()
        cate = data['车型'].unique().tolist()
        full_data = pd.DataFrame()
        for i in cate:
            cate_data = data[data['车型'] == i]
            cate_data.loc[cate_data['车长'].isnull(),'车长'] = cate_data.loc[data['车长'].notnull()]['车长'].median()
            full_data = full_data.append(cate_data)
        full_data = full_data.sort_values(by='Unnamed: 0',axis=0)
        full_data.drop('Unnamed: 0',axis=1,inplace=True)
        return full_data
    
    def mergeData(self,data,oil):
        data = pd.merge(data,oil,on=['日期','start_province'],how='left')
        return data

    def excute(self):
        data,oil = self.readFile()
        data = self.fillNA(data)
        data = self.mergeData(data,oil)
        return data