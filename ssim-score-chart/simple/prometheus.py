import prometheus_client

class PromMetrics:
    def __init__(self, app_port=8000):
        prometheus_client.start_http_server(app_port)
        # Prometheus metrics to collect
        ## ssim
        self.ssim_avg_gauge = prometheus_client.Gauge(
            "ssim_avg_gauge", "for visualizing ssim dot line chart",
            ["line", "model"])
        self.ssim_average_line = prometheus_client.Gauge(
            "ssim_past_average_line", "ssim of past period calculated average line by config",
            ["line", "model"])
        self.ssim_pos_one_sigma = prometheus_client.Gauge(
            "ssim_pos_one_sigma", "ssim of past period calculated one sigma value by average",
            ["line", "model"])
        ## ai score
        self.ai_score_avg_gauge = prometheus_client.Gauge(
            "ai_score_avg_gauge", "for visualizing AI score dot line chart",
            ["line", "model"])
        self.ai_score_average_line = prometheus_client.Gauge(
            "ai_score_past_average_line", "ai_score of past period calculated average line by config",
            ["line", "model"])
        self.ai_score_pos_one_sigma = prometheus_client.Gauge(
            "ai_score_pos_one_sigma", "ai_score of past period calculated one sigma value by average",
            ["line", "model"])
        # prometheus_client.write_to_textfile("/log.prom", self.REGISTRY)
