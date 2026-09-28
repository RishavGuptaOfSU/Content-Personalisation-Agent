FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Dev server bound to all interfaces so the container port mapping works.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
