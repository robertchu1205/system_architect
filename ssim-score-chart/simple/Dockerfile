FROM harbor-k8s.wzs.wistron.com.cn/datteam/python:3.7-alpine

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=TRUE
WORKDIR /app
COPY . .
EXPOSE 8000
ENTRYPOINT [ "python", "/app/main.py"]