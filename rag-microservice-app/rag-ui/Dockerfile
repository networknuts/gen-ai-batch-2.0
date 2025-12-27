FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy UI files
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

