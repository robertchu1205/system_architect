# Here is the build image
FROM harbor.wzs.wistron.com.cn/datteam/python:3.7-slim as builder

COPY requirements.txt /app/requirements.txt
WORKDIR app

# RUN pip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt
RUN pip install --user -r requirements.txt
COPY . /app

# Here is the production image
FROM harbor.wzs.wistron.com.cn/datteam/python:3.7-slim as app

COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /gw

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=TRUE
WORKDIR /gw
EXPOSE 3333

ENV PATH=/root/.local/bin:$PATH
# CMD ["gunicorn", "-c wsgi_config.py", "wsgi:app"]
ENTRYPOINT [ "sh", "/gw/sh_gw.sh" ]

# d build -t harbor.wzs.wistron.com.cn/datteam/aoi-wzs-p3-dip-prewave-saiap/gateway:slim-builder 
# /raid/data/robert/gateway/blueprints/ 
# -f /raid/data/robert/gateway/blueprints/Dockerfile.slim.builder 