FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY mon-app/package*.json ./

RUN npm ci

COPY mon-app/ ./

ARG VITE_APP_NAME="WATERCHALLENGE"
ARG VITE_ORGANIZATION="WATERCHALLENGE"
ARG VITE_API_BASE_URL="/api"
ARG VITE_COOKIE_SECRET="zKXr8pCRDoh13Y8f4kK7NNveOUFIJXmlkjdkk"

ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_ORGANIZATION=$VITE_ORGANIZATION
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_COOKIE_SECRET=$VITE_COOKIE_SECRET

RUN npm run build


FROM nginx:1.27-alpine AS runtime

COPY mon-app/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]