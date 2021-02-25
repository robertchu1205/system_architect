# gateway
    distributor dealing with images to be inferred
## routes:
- /metrics : statistical data for prometheus
- /predict : distributor api
- /showconfig : showing current temp config
- /config : html form for user to change confidence threshold by models
## functions
- parameters from config.yaml or config.json
- restful and grpc supported
- image encoded to base64 string and image in bytes array supported
- some custom functions seperated by calling api in gateway for easier implement
- all gateway info saved to prometheus format for dashboard in grafana
## monitoring visualization
<img src="../gateway-metrics-instant.png">
<img src="../gateway-metrics-analysis.png">