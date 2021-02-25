FROM harbor.wzs.wistron.com.cn/datteam/aoi-wzs-p3-dip-prewave-saiap/daily-metrics:builder AS builder
COPY . .

RUN go build -ldflags="-w -s" -o /builder

FROM scratch
COPY --from=builder /builder /dailymetrics
ENTRYPOINT ["/dailymetrics"]
EXPOSE 8080
# CMD ["/dailymetrics"]