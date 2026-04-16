# Frontend Dockerfile - Multi-stage build
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json .env .

# Install dependencies
RUN npm ci

# Copy source
COPY src/ ./src/
COPY public/ ./public/

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built app from build stage
COPY --from=build /app/build ./build

# Expose port
EXPOSE 3000

# Start application
CMD ["serve", "-s", "build", "-l", "3000"]
