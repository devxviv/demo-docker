FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files
COPY html /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# nginx starts automatically with the base image
