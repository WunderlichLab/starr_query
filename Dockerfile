FROM python:3.11-slim-bookworm

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    apache2-dev \
    libmariadb-dev \
    libmariadb3 \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/starr_query

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir mod_wsgi

# App source
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY starr_query.wsgi .

# Apache config
COPY apache/starr_query.conf /etc/apache2/sites-available/starr_query.conf

# Configure Apache to load the mod_wsgi built for this Python
RUN mod_wsgi-express module-config > /etc/apache2/mods-available/wsgi.load \
    && a2enmod wsgi headers \
    && a2ensite starr_query \
    && a2dissite 000-default

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]