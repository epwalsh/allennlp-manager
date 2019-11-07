FROM python:3.6-slim-stretch

RUN set -x \
    && apt-get update \
    && apt-get install -y \
        curl \
        build-essential \
        git \
        supervisor \
        nginx \
    && pip --no-cache-dir install --upgrade pip setuptools wheel \
    && rm -rf /var/lib/apt/lists/*

# Remove default nginx configurations
RUN rm -f /etc/nginx/nginx.conf && \
    rm -f /etc/nginx/conf.d/*.conf && \
    rm -f /etc/nginx/sites-enabled/*

# Create run pid path
RUN mkdir -p /run/nginx/

# Direct nginx logs to docker output
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Create nginx user
RUN adduser --system --no-create-home --shell /bin/false --group --disabled-login nginx

WORKDIR /opt/python/app/

COPY requirements.txt requirements.txt
RUN pip --no-cache-dir install -r requirements.txt
COPY requirements.server.txt requirements.server.txt
RUN pip --no-cache-dir install -r requirements.server.txt

COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY mallennlp mallennlp/

ARG COMMITHASH
ENV COMMITHASH ${COMMITHASH:-"unknown"}
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 5000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
