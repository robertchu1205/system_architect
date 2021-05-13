
#FROM tiangolo/uwsgi-nginx:python3.7
FROM repo.devpack.cc/mre200/oneai-process:base
RUN pip install flask

# URL under which static (not modified by Python) files will be requested
# They will be served by Nginx directly, without being handled by uWSGI
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /app/static

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
# ENV STATIC_INDEX 1
ENV STATIC_INDEX 0

# Make /app/* available to be imported by Python globally to better support several use cases like Alembic migrations.
ENV PYTHONPATH=/app
ADD . /flask-app
WORKDIR /flask-app

#EXPOSE 3000

ENTRYPOINT ["/flask-app/playrun.sh"]


