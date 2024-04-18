FROM golang:1.21.6 as base

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o bin/download_stocks .

FROM ubuntu:22.04 as final
USER root
RUN apt-get update && apt-get install -y ca-certificates iputils-ping telnet net-tools

USER 1001
WORKDIR /app
COPY --from=base /app/bin/ .

CMD ["sleep", "infinity"]