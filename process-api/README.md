# OneAI Process
## Getting Started (API server)
#### Step 1 Clone the code into a fresh folder
```
$ git clone https://gitlab.devpack.cc/mre200/oneai-process.git
$ cd oneai-process
```
#### Step 2 Install Dependencies.
```
$ pip install -r requirements.txt
```

#### Step 3 Start API server
```
$ python src/app.py
```
Swagger Docs: http://127.0.0.1:3000/apidocs/

## Getting Started (gRPC server)
#### Step 1 Clone the code into a fresh folder
#### Step 2 Install Dependencies.
#### Step 3 Start gRPC server
```
$ python src/app_server.py
```
#### Step 4 Try run gRPC service
```
$ python src/gRPC/client/app_client.py
```



## 說明
+ 本框架提供 API 依序執行使用者放置的前處理與後處理 function，第一個 function 的 output 會成為第二個 function 的 input，依此類推。API 將回傳最後一個 function 的 output。 
+ 前處理與後處理的 function 資料夾請分別置於 funcions/pre_process 與 funcions/post_process 的資料夾
```
┌ src
│   └ functions
│      ├─ pre_process
│      │  └─ funtion folder
│      └─ post_process
│         └─ funtion folder
```
+ 若該 function 需引用外部模組，請維護 requirements.txt 以供 function 在正式環境能順利執行
+ 若該 function 引用的模組已安裝，直接放入 funcions/pre_process 或 funcions/post_process 資料夾，無須重新啟動 API server 即可執行
+ 每個 function 的執行起始點為 handler.py 內的 handler class 的 execute function
```
┌ src
│   └ functions
│      ├─ pre_process
│      │  └─ funtion folder
│      │     └─ handler.py
```
```python=
# handler.py
class handler:
    def execute(input):
        result = input
        return result
```
+ 因動態載入模組限制，function 內部模組的引用請使用絕對路徑
```python=
# handler.py
from  functions.pre_process.ROI.util import calculate
class handler:
    def execute(input):
        return calculate.add(input)
```