# publisher/Dockerfile
FROM golang:latest AS build
WORKDIR /app
COPY . .
RUN go build -o /stock-publisher

FROM alpine:latest
WORKDIR /app
COPY --from=build /stock-publisher .
EXPOSE 8080
# Hier kannst du weitere ENV-Variablen definieren, wenn nötig
ENTRYPOINT ["/app/stock-publisher"]
