# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage (for docker-compose local)
FROM nginx:alpine AS local

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

# Cloud Run stage
FROM nginx:alpine AS cloudrun

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx template for Cloud Run (uses envsubst for BACKEND_URL)
COPY nginx.cloudrun.conf.template /etc/nginx/conf.d/default.conf.template

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Cloud Run requires port 8080
EXPOSE 8080

ENTRYPOINT ["/docker-entrypoint.sh"]
