# Imagen web de desarrollo: compila el frontend React/Vite y lo sirve con Nginx.
#
# Se usa desde docker-compose.yml (servicio `nginx`) con contexto ./frontend.
# Cada `docker compose up --build` recompila el código actual, así que nunca se
# sirve una compilación vieja de frontend/dist. La configuración de Nginx
# (nginx/nginx.conf) se monta desde el host para poder editarla en desarrollo.

FROM node:24-alpine AS build

WORKDIR /app

# Dependencias exactas del package-lock.json (capa cacheada mientras no cambien).
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# El cliente exige una URL absoluta sin barra final (src/lib/env.ts). Por
# defecto, el mismo origen que publica Nginx en desarrollo.
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_NAME=SGT-SIAAF
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_APP_NAME=${VITE_APP_NAME} \
    VITE_DEMO_MODE=false \
    VITE_USE_MOCKS=false

# `npm run build` = `tsc -b && vite build`: falla si hay errores de tipos.
RUN npm run build


FROM nginx:1.24-alpine AS web

COPY --from=build /app/dist /usr/share/nginx/html
