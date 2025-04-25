import requests
from simplekml import Kml
import time
from datetime import datetime, timedelta

api_key = '1c0fc8da4d1225f8032c2274aeac6c96'
des = ["拉萨贡嘎国际机场", "布达拉宫", "桑耶寺", "昌珠寺", "羊卓雍措景区", "卡若拉冰川", "江孜县", "扎什伦布寺", "热萨乡"]
deslotation = ['90.907599,29.294506', '91.118463,29.654471', '91.503730,29.323590', '91.773235,29.190684', '90.619256,29.190506', '90.166506,28.883271', '89.605654,28.911860', '88.871941,29.265392', '88.039323,29.084090']
# deslotation = []
adcode = ['540522', '540102', '540521', '540502', '540531', '540222', '540222', '540202', '540225']
weather = []

def get_amap_route(origin, destination):
    url = f"https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&key={api_key}"
    response = requests.get(url).json()
    path = response["route"]["paths"][0]["steps"]
    coords = []
    for step in path:
        coords.extend([tuple(map(float, point.split(","))) for point in step["polyline"].split(";")])
    return coords

def get_GPSandADCode(address):
   
    url = f" https://restapi.amap.com/v3/geocode/geo?address={address}&key={api_key}"
    data = requests.get(url).json()
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city=110101&key={api_key}"
    data2 = requests.get(url).json()
    {'status': '1', 'info': 'OK', 'infocode': '10000', 'count': '1', 'geocodes': [{'formatted_address': '西藏自治区山南市贡嘎县拉萨贡嘎国际机场', 'country': '中国', 'province': '西藏自治区', 'citycode': '0893', 'city': '山南市', 'district': '贡嘎县', 'township': [], 'neighborhood': {'name': [], 'type': []}, 'building': {'name': [], 'type': []}, 'adcode': '540522', 'street': [], 'number': [], 'location': '90.907599,29.294506', 'level': '兴趣点'}]}
    if data["status"] == "1" and int(data["count"]) > 0:
        location_str = data["geocodes"][0]["location"]
        adcode = data["geocodes"][0]["adcode"]
        longitude, latitude = location_str.split(",")
        return location_str,adcode
    return data



def DseToGPS():
    for i in des:
        # print(i)
        gps,code = get_GPSandADCode(i)
        time.sleep(1)
        # print(result)
        deslotation.append(gps)
        adcode.append(code)

def get_weather_forecast(adcode, days=3):
    """
    获取未来天气预报
    :param adcode: 区域编码
    :param api_key: 高德API Key
    :param days: 预报天数(1-7)
    :return: 天气数据列表
    """
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    # 获取未来日期
    future_dates = [(datetime.now() + timedelta(days = 4)).strftime("%Y-%m-%d")]
    # future_dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, days+2)]
    weather_data = []
    for date in future_dates:
        params = {
            "key": api_key,
            "city": adcode,
            "extensions": "all",  # 获取预报数据
            "output": "JSON"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            print(data)
            if data["status"] == "1" and data["forecasts"]:
                # 查找指定日期的预报
                for forecast in data["forecasts"][0]["casts"]:
                    if forecast["date"] == date:
                        forecast["adcode"] = adcode
                        weather_data.append(forecast)
                        break
        except Exception as e:
            print(f"获取{date}天气失败: {str(e)}")
    
    return weather_data

def save_weather_to_kml(weatherset, gpsset, output_file):
    """
    将天气数据保存为KML文件
    :param weather_data: 天气数据列表
    :param output_file: 输出文件名
    """
    kml = Kml()
    
    for i in range(len(weatherset)):
        weather = weatherset[i][0]
        gps = gpsset[i]
        # 为每个预报点创建Placemark
        name=f"{weather['date']}天气"
        point = kml.newpoint(name=f"{weather['date']}天气")
        
        # 使用adcode对应的中心坐标（这里简化处理，实际应用中应该查询adcode对应的坐标）
        # 实际应用中应该调用高德地理编码API获取adcode对应的坐标
        point.coords = [tuple(map(float, gps.split(",")))] # 示例坐标，北京中心
        
        # 添加天气信息到描述中
        description = f"""
        <![CDATA[
        <h2>{weather['date']}天气预报</h2>
        <p>白天天气: {weather['dayweather']}</p>
        <p>夜间天气: {weather['nightweather']}</p>
        <p>白天温度: {weather['daytemp']}℃</p>
        <p>夜间温度: {weather['nighttemp']}℃</p>
        <p>白天风向: {weather['daywind']} 风力: {weather['daypower']}</p>
        <p>夜间风向: {weather['nightwind']} 风力: {weather['nightpower']}</p>
        ]]>
        """
        point.description = description
        
        # 根据天气类型设置图标样式
        if "雨" in weather['dayweather']:
            point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pal3/icon21.png"
        elif "晴" in weather['dayweather']:
            point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pal3/icon39.png"
        elif "云" in weather['dayweather']:
            point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pal3/icon22.png"
        else:
            point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/pal2/icon57.png"
    
    kml.save(output_file)
    print(f"天气数据已保存到 {output_file}")

# DseToGPS()
print(deslotation)
print(adcode)
kml = Kml()
# for i in range(len(deslotation)-1):
#     print(des[i], des[i+1])
#     route_coords = get_amap_route(deslotation[i], deslotation[i+1])
#     linestring = kml.newlinestring(name="高德导航路线")
#     linestring.coords = route_coords  # 填入上一步获取的坐标
#     time.sleep(1)
# kml.save("amap_route.kml")
DAYS = 3
for i in range(len(adcode)):
    weather.append(get_weather_forecast(adcode[i], deslotation))
print(weather)
save_weather_to_kml(weather, deslotation,'weather.kml')
# route_coords = get_amap_route("116.404,39.915", "116.406,39.917", api_key)
# kml = Kml()
# linestring = kml.newlinestring(name="高德导航路线")
# linestring.coords = route_coords  # 填入上一步获取的坐标
# kml.save("amap_route.kml")