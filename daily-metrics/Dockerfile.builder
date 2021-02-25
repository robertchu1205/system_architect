FROM golang:1.13

ENV GOOS linux
ENV GOARCH amd64
ENV CGO_ENABLED 0
ENV GOPATH ""
ENV GOPROXY "https://goproxy.io,direct"

COPY . .

# prevent curl 18 error
RUN git config --global http.postBuffer 524288000
RUN go get -d -t -v