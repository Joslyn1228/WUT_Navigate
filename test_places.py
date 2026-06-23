import requests

# 测试场所API
r = requests.get('http://localhost:8000/api/places')
print('场所API状态:', r.status_code)
places = r.json()
print('场所数量:', len(places))
print('\n场所列表:')
for p in places:
    print(f"  - {p['name']}: ({p['latitude']}, {p['longitude']}) [{p['category']}]")

# 测试附近场所API（使用南湖图书馆附近坐标）
r2 = requests.get('http://localhost:8000/api/nearby?lat=30.5067&lng=114.3792&radius=500')
print('\n附近场所API状态:', r2.status_code)
data = r2.json()
print('附近场所数量:', len(data.get('nearby_places', [])))
if 'nearby_places' in data:
    for np in data['nearby_places']:
        print(f"  - {np['place']['name']}: {np['distance']:.1f}米")
