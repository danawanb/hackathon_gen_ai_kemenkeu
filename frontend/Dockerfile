FROM node:lts-alpine as build
WORKDIR /app
COPY ./package*.json ./
RUN npm install
COPY . .
ENV NODE_OPTIONS="--max_old_space_size=1080"
RUN npm run build

FROM node:lts-alpine AS production
COPY --from=build /app/build .
COPY --from=build /app/package.json .
COPY --from=build /app/package-lock.json .
RUN npm ci --omit=dev
ENV API_BASE_URL="http://localhost:8000"
EXPOSE 3000
CMD ["node", "."]
