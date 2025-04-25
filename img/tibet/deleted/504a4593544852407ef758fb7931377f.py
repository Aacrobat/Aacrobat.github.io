import requests
from simplekml import Kml
def get_amap_route(origin, destination, api_key):
    url = f"https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&key={api_key}"
    response = requests.get(url).json()
    path = response["route"]["paths"][0]["steps"]
    coords = []
    for step in path:
        coords.extend([tuple(map(float, point.split(","))) for point in step["polyline"].split(";")])
    return coords

api_key = '1c0fc8da4d1225f8032c2274aeac6c96'  # 替换为你的Key
route_coords = get_amap_route("116.404,39.915", "116.406,39.917", api_key)
kml = Kml()
linestring = kml.newlinestring(name="高德导航路线")
linestring.coords = route_coords  # 填入上一步获取的坐标
kml.save("amap_route.kml")