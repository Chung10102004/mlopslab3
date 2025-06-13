# MSSV
22520390

22520189

22520084

22520033

22520161

# Demo lab2
## Demo Docker compose
[![Watch the video](https://img.youtube.com/vi/MQs76C55yxY/0.jpg)](https://www.youtube.com/watch?v=MQs76C55yxY)
## Demo Docker hub
[![Watch the video](https://img.youtube.com/vi/5omD_OBICUA/0.jpg)](https://youtu.be/5omD_OBICUA)
## Demo on server
[![Watch the video](https://img.youtube.com/vi/YZUyILdbjpE/0.jpg)](https://youtu.be/YZUyILdbjpE )

# Tải và chạy
## Bằng Docker compose 

Đầu tiên ta clone code về
``` 
git clone https://github.com/Chung10102004/mlopslab2.git
cd mlopslab2
```
Tiếp theo ta build và chạy API 
```
docker-compose up --build 
```
## Bằng Docker hub [link](https://hub.docker.com/r/chung10102004/mlopslab2)
Đầu tiên ta pull image về bằng lệnh
```
docker pull chung10102004/mlopslab2:1.0.0
```
Tiếp theo ta chạy container bằng lệnh 
```
docker run -p 8888:8888 chung10102004/mlopslab2:1.0.0
```
# Sử dụng và test API
Để sử dụng API ta cần request tới sever một input là file json có format 

`
{
"features" : "string input"
}
`
Dưới đây là 1 đoạn code để có thể test thử API nhanh : 
~~~ python
import requests
import json
input = {"features": "normal"}

url = "http://127.0.0.1:8888/predict" # change your IP sever
data = json.dumps(input)

repposense = requests.post(url, data)
print(repposense.json())
~~~
Output:

`["Predictions": "0"]`[^1]
[^1]: 0 là positive, 1 là neural, 2 là positive.

