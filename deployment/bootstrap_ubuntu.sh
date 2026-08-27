#!/usr/bin/env bash

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Run as root."
    exit 1
fi

apt update

apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    certbot \
    python3-certbot-nginx

if ! id aeroesp >/dev/null 2>&1; then
    useradd \
        --system \
        --create-home \
        --home-dir /var/www/aeroesp \
        --shell /bin/bash \
        aeroesp
fi

mkdir -p /var/www/aeroesp
mkdir -p /etc/aeroesp
mkdir -p /var/backups/aeroesp

chown -R aeroesp:www-data /var/www/aeroesp
chown root:aeroesp /etc/aeroesp

chmod 750 /etc/aeroesp

echo "AeroESP server base prepared."