# ============================
# 1. Build stage
# ============================
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the React app
RUN npm run build


# ============================
# 2. Production stage (serve static files)
# ============================
FROM nginx:alpine

# Copy build output to Nginx html folder
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx config (optional, e.g., for React Router fallback)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
