from DSSATTools import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

# ! 先模擬一個期作: 110-1 台南11號田區  C5 N = 220
DATES = pd.date_range('2021-03-02', '2021-06-23')
N = len(DATES)
weather_file_path = r'110I 氣象資料0302-0623 - 補0616-0620雨量.xlsx'
df = pd.read_excel(weather_file_path)
dt_filters = (df['時間'].isin(DATES))
# X_list = ['絕對最低氣溫(℃)', '絕對最低氣溫(℃)', '累積降水量(mm)', '全天空日射量', '平均相對溼度(%)']
dt = df[dt_filters]
print(dt.shape)
# dt = pd.DataFrame(dt, index=dt['時間'])
dt = pd.DataFrame(
    {
    '絕對最低氣溫(℃)': dt['絕對最低氣溫(℃)'].values,
    '絕對最高氣溫(℃)': dt['絕對最高氣溫(℃)'].values,
    '累積降水量(mm)': dt['累積降水量(mm)'].values,
    '累積日射量(MJ/m2)': dt['累積日射量(MJ/m2)'].values,
    '平均相對溼度(%)': dt['平均相對溼度(%)'].values,
    },
    index = DATES
)
# Create a WeatherData instance
WTH_DATA = WeatherData(
    dt,
    variables={
        '絕對最高氣溫(℃)': 'TMAX', '絕對最低氣溫(℃)': 'TMIN', 
        '累積降水量(mm)': 'RAIN', '累積日射量(MJ/m2)': 'SRAD',
        '平均相對溼度(%)': 'RHUM'
    }
)
dt.to_csv('weather.csv')

print(WTH_DATA)

# Create a WheaterStation instance
wth = WeatherStation(
    WTH_DATA, 
    {'ELEV': 33, 'LAT': 0, 'LON': 0, 'INSI': 'TARI'}
)

soil = SoilProfile()
soil.add_layer(SoilLayer(25,pars={
    'SLCF': 33.24, # 粗顆粒物 (>2 mm)，單位為%
    'SLSI': 44.71, # 粉砂（0.05 至 0.002 mm），單位為%
    'SLCL': 22.05, # 黏土 (<0.002 mm)，單位為%
    'SLHW': 5.51,  # 水中的 pH 值
    'SLNI': 0.12, # 總氮，單位為%
    'SLPX': 31.05, # 提取性磷，單位為 mg kg-1
    'SLNA': 18.26, # 鈉，單位為 cmol kg-1
    'SLKE': 52.83, # 可交換鉀，cmol kg-1 IB
    'SLCA': 715.35, # 鈣，可交換性，單位為 cmol kg-1
    'SLMG': 134.93, # 鎂，單位為 cmol kg-1
    'SLMN': 1.34, # 錳
    'SLEC': 90.5, # 電導率，單位為 seimen
    'SLOC': 1.58, # 有機碳，單位為%
}))

# !初始化土壤環境 銨態氮、硝酸態氮含量
soil.NH4ppm = 1.44
soil.NO3ppm = 8.48

crop = Crop('rice')
crop.cultivar['00TN11'] = {
    'VAR-NAME........': 'TN11',
    'EXPNO': '.',
    'ECO#': 'IB0001',
    'P1': 900, # 643.1
    'P2R': 250, # 123.4
    'P5': 900, # 531.2
    'P2O': 12, # 11.26
    'G1': 100, # 37.99
    'G2': 0.03, # 0.026
    'G3': 2.0, # 1.501
    'PHINT': 83.0,
    'THOT': 28.0,
    'TCLDP': 15.0,
    'TCLDF': 15.0,
}

# !新增品種資料的話，要先執行寫入檔案的動作，指定到基因型資料中
crop.write('./DSSATTools_notebooks/DSSAT/static/Genotype')

# ! 建立管理物件
man = Management(
    cultivar='00TN11',
    planting_date=DATES[1],
    irrigation='R',
    fertilization='R',
    harvest='M',
)

def yyyymmdd_to_doy(date_str):
    """
    將日期字符串轉換為DOY
    date_str: YYYMMDD日期字符串，例如'20220317'
    return: 該日期的DOY，整數格式
    """
    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:])
    dt = datetime(year, month, day)
    doy = str(dt.timetuple().tm_yday).zfill(3)
    return doy

# !建立施肥策略
# FDATE: 施肥日期，格式為YYYYDDD，其中YYYY表示年份，DDD表示當年的第幾天。
FDATE = [date[2:4] + yyyymmdd_to_doy(date) for date in ['20210303', '20210317', '20210331', '20210429']]
print(f'DOY_list = {FDATE}')
# FMCD: 施肥物料的代碼，與DSSAT中的肥料庫存檔案相關。
FMCD = [100, 100, 100, 100]
# FACD: 施肥方法代碼。
FACD = [1, 4, 4, 4]
# FDEP: 施肥深度（單位：厘米）。
FDEP = [15, 0, 0, 0]
# FAMN: 施加的氮量（單位：千克氮每公頃）。
FAMN = [30, 53.3, 53.3, 53.3]
# FAMP: 施加的磷量（單位：千克磷每公頃）。
FAMP = [0, 0, 0, 0]
# FAMK: 施加的鉀量（單位：千克鉀每公頃）。
FAMK = [0, 0, 0, 0]
# FAMC: 施加的有機碳量（單位：千克每公頃）。
FAMC = [0, 0, 0, 0]
# FAMO: 施加的有機物量（單位：千克每公頃）。
FAMO = [0, 0, 0, 0]
# FOCD: 施肥有機碳含量（單位：％）。
FOCD = [0, 0, 0, 0]
# FERNAME: 施肥物料的名稱。
FERNAME = [None, None, None]
data = list(zip(FDATE, FMCD, FACD,FDEP,FAMN,FAMP,FAMK,FAMC,FAMO,FOCD,FERNAME))
schedule = pd.DataFrame(data, columns = ['FDATE', 'FMCD', 'FACD','FDEP','FAMN','FAMP','FAMK','FAMC','FAMO','FOCD','FERNAME'])

man.fertilizers['table'] = TabularSubsection(schedule)
man.simulation_controls['FERTI'] = 'R'
man.simulation_controls['VBOSE']= 'Y' #- 是否輸出詳細的模擬資訊。
man.simulation_controls['CHOUT']= 'Y' #- 是否輸出化學物質資料。
man.simulation_controls['OPOUT']= 'Y' #- 是否輸出其它類型的結果。
man.simulation_controls['FMOPT']= 'A' #- 輸出檔案的模式，A 表示追加模式。


# !建立灌溉時間與灌溉量時程表
DATES = DATES
irrig = [999 for i in range(len(DATES))]
data = list(zip(DATES, irrig))
schedule = pd.DataFrame(data, columns = ['date', 'IRVAL'])

# !這邊把日期變成日數了
schedule['IDATE'] = schedule.date.dt.strftime('%y%j')

# Code to define the irrigation operation
# !定義灌溉施作編號?
schedule['IROP'] = 'IR001'
schedule = schedule[['IDATE', 'IROP', 'IRVAL']]

print(dir(man))

# # !灌溉時間排程
man.irrigation['table'] = TabularSubsection(schedule)
# # !設定為依照reported schedule灌溉
man.simulation_controls['IRRIG'] = 'R'

# # !成熟時收割
man.simulation_controls['HARVS'] = 'M'


# !進行模擬
dssat = DSSAT()
# dssat.setup(r'G:\111_Smart_Agri\DSSATTools_notebooks\DSSAT')
dssat.setup()
dssat.run(soil=soil, weather=wth, crop=crop, management=man)
# Run and check the final Yield

print(dssat.output)
print(dir(dssat))
print(type(dssat.output))
print(dssat.output['PlantGro'].columns)

output = dssat.output['PlantGro']
output.to_excel('./DSSATTools_notebooks/TN11_1101_C5_Result.xlsx')
target_output = 'CWAD'

X = output.DTTC
y = eval(f'output.{target_output}')
unit = '(kg / ha)'
# Ground truth
GT_X = [425.5, 605.9, 838.8]
GT_y = [1180, 2500, 7170]
plt.plot(X, y, label='Predict')
plt.plot(GT_X, GT_y, '*', label='Ground Truth')
plt.xlabel('DTTC (Cumulative growing degree days)')
plt.ylabel(f'{target_output} {unit}')
plt.title(f'Crop Dry Weight kg/ha')
plt.show()
