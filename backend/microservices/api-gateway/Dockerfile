FROM node:24-slim AS base

WORKDIR /usr/src/app

COPY ./package.json ./package-lock.json ./

FROM base AS builder

# copying package.json files to install dependnecies
COPY ./libs/ts/common/package.json ./libs/ts/common/
COPY ./libs/ts/contracts/package.json ./libs/ts/contracts/
COPY ./microservices/api-gateway/package.json ./microservices/api-gateway/

RUN npm ci -w common -w contracts -w api-gateway

# copying app and libs source code
COPY ./libs/ts/ ./libs/ts
COPY ./libs/proto ./libs/proto
COPY ./microservices/api-gateway ./microservices/api-gateway

# bulding libs and api-gateway app only
RUN npm run build -w common -w contracts -w api-gateway

FROM base AS dev

# copying node_modules from builder stage to decrease image size and speed up builds
COPY --from=builder /usr/src/app/node_modules/ ./node_modules

COPY --from=builder /usr/src/app/libs/ts/ ./libs/ts
COPY --from=builder /usr/src/app/libs/proto ./libs/proto
COPY --from=builder /usr/src/app/microservices/api-gateway ./microservices/api-gateway

WORKDIR /usr/src/app/microservices/api-gateway

CMD ["npx", "nest", "start", "--watch"]

FROM base AS prod

ENV NODE_ENV=production

COPY --from=builder /usr/src/app/microservices/api-gateway/healthcheck.js ./microservices/api-gateway/
COPY --from=builder /usr/src/app/microservices/api-gateway/oauth-tenant-public-key.pem ./microservices/api-gateway/

COPY --from=builder /usr/src/app/microservices/api-gateway/package.json ./microservices/api-gateway/
COPY --from=builder /usr/src/app/microservices/api-gateway/dist ./microservices/api-gateway/dist/

COPY --from=builder /usr/src/app/libs/ts/common/package.json ./libs/ts/common/
COPY --from=builder /usr/src/app/libs/ts/common/dist  ./libs/ts/common/dist/

COPY --from=builder /usr/src/app/libs/ts/contracts/package.json ./libs/ts/contracts/
COPY --from=builder /usr/src/app/libs/ts/contracts/dist  ./libs/ts/contracts/dist/
COPY --from=builder /usr/src/app/libs/proto ./libs/proto

RUN npm ci --omit=dev -w common -w contracts -w api-gateway

USER node

WORKDIR /usr/src/app/microservices/api-gateway

CMD ["node", "./dist/src/main.js"]