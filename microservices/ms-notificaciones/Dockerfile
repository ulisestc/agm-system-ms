FROM node:20-alpine
WORKDIR /app

COPY microservices/ms-notificaciones/package*.json ./

RUN npm install

COPY microservices/ms-notificaciones/ .

COPY proto/ /proto/

EXPOSE 50056
CMD ["npm", "start"]