FROM python:3.11-alpine

WORKDIR /app

# Install dependencies (cronie)
RUN apk add --no-cache busybox-openrc && \
    pip install --no-cache-dir tomli tomli_w

# Copy script and entrypoint
COPY update_continuwuity.py /app/update_continuwuity.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run as root
USER root
ENTRYPOINT ["/entrypoint.sh"]