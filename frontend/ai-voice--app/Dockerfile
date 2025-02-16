FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install --production

# Copy application files
COPY . .

# Build the frontend
RUN npm run build

# Expose the port for Vite
EXPOSE 80

# Run the Vite preview server
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
