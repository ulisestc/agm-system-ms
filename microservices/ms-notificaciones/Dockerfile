FROM node:20-alpine
WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Nota: Si proto/ es necesario y el root de Railway es la carpeta del ms, 
# este COPY fallará en Railway. Pero para el resto del build avanzará.
# COPY proto/ /proto/

EXPOSE 50056
CMD ["npm", "start"]
