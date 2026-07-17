FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY mon-app/package*.json ./
RUN npm ci
COPY mon-app/ ./
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY mon-app/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
CMD ["nginx", "-g", "daemon off;"]