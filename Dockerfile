FROM python:3.11-slim

## System dependencies 
# apache2
# libapache2-mod-wsgi-py3
# libmariadb-dev + libmariadb3
# gcc / pkg-config
RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-wsgi-py3 \
    libmariadb-dev \
    libmariadb3 \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies 
WORKDIR /var/www/starr_query
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application source code
COPY app.py        .
COPY ca.pem        .
COPY templates/    templates/
COPY static/       static/

# WSGI entry point
COPY starr_query.wsgi .

# Apache virtual host config
COPY apache/starr_query.conf /etc/apache2/sites-available/starr_query.conf

# Enable mod_wsgi and our site, disable the default site
RUN a2enmod wsgi \
    && a2ensite starr_query \
    && a2dissite 000-default

EXPOSE 80

# Env var placeholders (BU injects real values at runtime)
ENV DB_HOST=""
ENV DB_USER=""
ENV DB_PASS=""
ENV DB_NAME=""
ENV DB_PORT="3306"

# Start Apache in the foreground so the container stays alive
CMD ["apache2ctl", "-D", "FOREGROUND"]