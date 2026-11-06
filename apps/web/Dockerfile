FROM nginxinc/nginx-unprivileged:1.29-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html styles.css app.js /usr/share/nginx/html/

# Generate stable content-based asset URLs at image build time. No manual bump needed.
RUN set -eu; \
    cd /usr/share/nginx/html; \
    js_version="$(sha256sum app.js | cut -c1-16)"; \
    css_version="$(sha256sum styles.css | cut -c1-16)"; \
    sed -i "s/__JS_VERSION__/${js_version}/g; s/__CSS_VERSION__/${css_version}/g" index.html; \
    ! grep -q "__JS_VERSION__\|__CSS_VERSION__" index.html

EXPOSE 8080
