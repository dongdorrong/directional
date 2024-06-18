# This Docker image is used for communication tests and database tests in a Kubernetes environment
FROM alpine

RUN apk update && \
    apk add --no-cache curl postgresql-client mysql-client && \
    curl -L -Ss https://github.com/cloverstd/tcping/releases/download/v0.1.1/tcping-linux-amd64-v0.1.1.tar.gz -o /tmp/tcping-linux.tgz && \
    tar zxf /tmp/tcping-linux.tgz -C /usr/local/bin && \
    chown root.root /usr/local/bin/tcping && \
    chmod 755 /usr/local/bin/tcping && \
    rm -rf /tmp/tcping-linux.tgz

CMD ["tail", "-f", "/dev/null"]
