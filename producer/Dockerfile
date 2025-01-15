FROM golang:1.20-alpine AS build
WORKDIR /app
COPY . .
# Achte darauf, dass in go.mod "go 1.20" (ohne Patch-Level) steht
RUN go build -o /stock-publisher

FROM alpine:3.17
WORKDIR /app
COPY --from=build /stock-publisher .
EXPOSE 8080
ENTRYPOINT ["/app/stock-publisher"]
