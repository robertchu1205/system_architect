### kustomization
- for easier yaml as template
- apply resources at the same time

### where and purpose
- [attempting](./attempting/)
    - tried & abandoned
- [base](./base/)
    - in ai servers
    - have to be deployed in A4
    - [daily metics](./base/daily-metrics/base/)
        - [daily metics](./base/daily-metrics/base/ftp-metrics.yaml)
            - optional
            - metrics used in dashboard **"FTP Daily Metrics, Loki Overkill & Leak Details"**
            - record and calculate overkill & leak rate from defined ftp
            - It would also record overkill & leak paths in **label** of the metircs
            - expose metrics thru prometheus
        - [file server](./base/daily-metrics/base/file-server.yaml)
            - optional
            - 1. pull labeled images by the date from data center
            - 2. to show overkill & leak images in the dashboard thru python.http.server
    - [gateway](./base/gateway/)
        - [base](./base/gateway/base/)
            - simple template for applying gateway
        - [overlay](./base/gateway/overlay/)
            - continuously pulling from gitlab: 2 containers in a deployment (pulling config & checkpoints and gateway)
            - sftp mounted directory: let users alter gateway config by editing files in sftp
            - both methods mentioed above were abandoned except p3 dip project with saiap
            - cases by projects and methods
    - [grafana](./base/grafana/base/)
        - [config](./base/grafana/base/config/)
        - [dashboard](./base/grafana/base/dashboards/)
            - previous dashboard json files template 
                - [p3 dip gateway metrics](./base/grafana/base/dashboards/P3-DIP-Prewave-AOI-INFA.json)
                - [metrics of p1 dip gateway deployed by oneai](./base/grafana/base/dashboards/Oneai-gateway-INFA.json)
                - [Overkill & Leak from daily metrics](./base/grafana/base/dashboards/FTP-Metrics-P3-DC.json)
                - [Overkill & leak's logs and images](./base/grafana/base/dashboards/Loki-lowlight-log.json)
                - [node exporter](./base/grafana/base/dashboards/node-exporter-full_rev19.json)
                - [confidence alerting](./base/grafana/base/dashboards/confidence-alerting.json)
        - troubleshooting
            - every password been set not worked for login:
                - ```Bash
                    # executed in container and reset password thru "grafana-cli"
                    /usr/share/grafana/bin/grafana-cli admin reset-admin-password 1q2w3e4r
                  ```
    - [loki](./base/loki/base/)
        - aggregate logs from promtail
        - [config](./base/loki/base/config.yml): mainly just kept the same setting
    - [promtail](./base/promtail/base/)
        - collect logs from containers' logs
        - must have privileges of **hostPath**
            - [rbac](./base/promtail/base/rbac.yaml): create special ServiceAccount of being able to access hostPath
        - [config](./base/promtail/base/config.yaml)
            - **clients - url**: loki api for promtail to push collected logs
            - **scrape_configs - static_configs - targets & labels**: specify which logs to collect
            - **scrape_configs - pipeline_stages**: have to be the order of "docker, json, labels"; **labels** for user to choose in the dashboard
    - [node exporter](./base/node-exporter/node-exporter-daemonset.yaml)
        - official daemonset yaml file: mainly just kept the same setting
    - [promtheus](./base/promtheus/)
        - [base](./base/promtheus/base/): easier method
            - [config](./base/promtheus/base/prometheus.yml) specified metrics from
                - scrape_configs 
                    - job_name: metrics collected with key "job", value "job_name"
                    - scrape_interval: intervals to update
                    - metrics_path: api endpoint
                    - static_configs
                        - targets: {service name}.{namespace}.svc.cluster.local
        - [base-service-monitor](./base/promtheus/base-service-monitor/): harder method
            - used in dgx2, p1-dip ai server
            - podmonitor and servicemonitor replacing config
    - [storage](./base/storage/)
        - [pv ai-log in librabig](./base/storage/log/)
            - yaml for deploying pv and pvc
        - [StorageClass](./base/storage/sc.yaml) template
        - [local path provisioner](./base/storage/local-path-provisioner.yaml) for init k8s servers
    - [tfserving](./base/tfserving/)
        - [base](./base/tfserving/base/)
            - simple template for applying tensorflow serving
        - [overlay](./base/tfserving/overlay/)
            - continuously pulling from gitlab: 2 containers in a deployment (pulling models and serving)
            - sftp mounted directory: let users update models by editing files in sftp
            - both methods mentioed above were abandoned except p3 dip project with saiap
            - cases by projects and methods
- [dev](./dev/)
    - in training servers (dgx2)
    - [data backup](./dev/data-backup/base/)
        - template is in dgx2 ( /raid/data/aoi-wzs-p1-dip-fa-nvidia; /raid/data/aoi-wzs-p3-dip-prewave-saiap )
        - backup target directory thru cronjob in case lose of data
    - [gateway test](./dev/gateway/)
        - in dgx2
    - [gitlab runner](./dev/gitlab-runner/)
        - in dgx2
        - deployment here used in repo "oneai", "aoi-wzs-p1-dip-fa-nvidia", "aoi-wzs-p3-dip-prewave-saiap"
    - [image dataset db](./dev/image-dataset-db/)
        - in dgx2
        - mariadb
    - [jupyter notebook](./dev/jupyter/base/)
        - in dgx2
    - [monitoring](./dev/monitoring/)
        - showed [here](10.41.241.230:30000) in dgx2
    - [pull from ftp](./dev/pull-ftp/base/)
        - in dgx2
        - pull **labeled** images for training and inserting to image db thru cronjob
    - [tensorflow serving](./dev/tensorflow-serving/)
        - [to create warmup assets](./dev/tensorflow-serving/create_tf_serving_warmup_requests.py)
            - in case requesting answers from tensorflow serving thru grpc delayed for the first time
            - would not happened in restful method
        - [served one model](./dev/tensorflow-serving/one-model-test.yaml)
            - in dgx2
        - [served multi-models](./dev/tensorflow-serving/dgx2-tfserving.yaml)
            - in dgx2
        - [test auto pulling files from gitlab container](./dev/tensorflow-serving/dgx2-tfserving.yaml)
            - abandoned
- [overlay](./overlay/)
    - kustomization
    - deploy combined services in a batch 
    - [wcd deployment](./overlay/inference/aoi-wcd-fa-saiap/)
        - tensorflow serving & gateway deployment in wcd
    - [monitoring](./overlay/monitoring/)
        - deploy promtail, loki, prometheus, grafana in a kustomization
- [ssim confidence monitoring](https://gitlab-k8s.wzs.wistron.com.cn/10802014/aoi-wih-ssim-monitoring)
    - calculate data from db and expose metrics thru prometheus with method **"spc control chart"**
    - monitor both ai confidence and ssim score
    - query **join** took too long
    - Gauge **ssim_avg_gauge, ai_score_avg_gauge** saved random 5 scores in last an hour
    - Gauge **ssim_average_line; ai_score_average_line** the average of every 5 scores in an hour within defined time range
    - Gauge **ssim_pos_one_sigma; ai_score_pos_one_sigma** a sigma of every 5 scores in an hour within defined time range