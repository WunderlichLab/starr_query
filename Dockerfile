FROM debian:stable-slim

# Install Apache, mod_wsgi (Python 3), and minimal build deps for mariadb client
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        apache2 \
        libapache2-mod-wsgi-py3 \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        libmariadb-dev-compat \
        libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install (global site-packages)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Apache site configuration
COPY apache-flask.conf /etc/apache2/sites-available/000-default.conf

# WSGI entrypoint for mod_wsgi
COPY wsgi.py /app/wsgi.py

# Ensure static files are readable
RUN chown -R www-data:www-data /app

# Enable needed Apache modules
RUN a2enmod wsgi headers

# Expose Apache’s port
EXPOSE 80

# Run Apache in foreground (required for container)
CMD ["apachectl", "-D", "FOREGROUND"]