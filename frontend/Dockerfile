# Use the official Node.js image as base
FROM node:18-alpine

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy all files to the container
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Run Vite dev server and ensure it binds to all interfaces
CMD ["npm", "run", "dev", "--", "--host"]