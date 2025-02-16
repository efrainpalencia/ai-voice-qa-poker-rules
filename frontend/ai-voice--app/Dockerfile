FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install --production

# Copy the rest of the application
COPY . .

# Build the frontend
RUN npm run build

# Expose port for the frontend
EXPOSE 5173

# Run the frontend application
CMD ["npm", "run", "preview"]