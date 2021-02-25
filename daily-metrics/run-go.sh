# git config --global http.postBuffer 524288000
# go get -d -t -v

# go mod init gitlab-k8s.wzs.wistron.com.cn/aoi-wzs-p3-dip-prewave-saiap/daily-metrics
# go install .

go run .

# go build -ldflags="-w -s" -o .
# ./daily-metrics
# go clean