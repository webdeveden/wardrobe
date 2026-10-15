FROM oven/bun:1.2-alpine AS build

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .

# "/api" means the browser calls the same origin and nginx proxies to the backend.
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN bun run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
