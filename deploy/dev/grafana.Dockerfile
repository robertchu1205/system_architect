ARG GRAFANA_VERSION="latest"

FROM harbor.wzs.wistron.com.cn/datteam/grafana/grafana:${GRAFANA_VERSION}-ubuntu

USER grafana

ARG GF_INSTALL_PLUGINS=""

RUN if [ ! -z "${GF_INSTALL_PLUGINS}" ]; then \
    OLDIFS=$IFS; \
        IFS=','; \
    for plugin in ${GF_INSTALL_PLUGINS}; do \
        IFS=$OLDIFS; \
        grafana-cli --pluginsDir "$GF_PATHS_PLUGINS" plugins install ${plugin}; \
    done; \
fi

# docker build --build-arg "GRAFANA_VERSION=7.0.0" --build-arg "GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-image-renderer"  -t harbor.wzs.wistron.com.cn/datteam/grafana/grafana:7.0.0-ubuntu-custom -f grafana.Dockerfile .