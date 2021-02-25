FROM harbor.wzs.wistron.com.cn/datteam/python:3.7

# RUN apt-get update \
# && apt-get install -y libsm6 libxext6 libxrender-dev \
# && apt-get clean

COPY requirements.txt /

# --no-cache-dir
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r /requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=TRUE
WORKDIR /gw
COPY . .
EXPOSE 3333
ENTRYPOINT [ "sh", "/gw/sh_gw.sh" ]

# docker build -t p3-saiap-gateway:flask-V2020-04-15 ./flask_gw

# d run --rm -it -v /home/robert/robertnb/gateway/:/config 
# -v /home/robert/robertnb/tfs-test/checkpoint/:/checkpoint -p 3333:3333 
# p3-saiap-gateway:flask-V2020-04-15