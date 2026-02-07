FROM node:20-alpine AS build
ARG BUILD_SCRIPT=build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run $BUILD_SCRIPT

FROM nginx:alpine AS local
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

FROM nginx:alpine AS cloudrun
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.cloudrun.conf.template /etc/nginx/conf.d/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/docker-entrypoint.sh"]
