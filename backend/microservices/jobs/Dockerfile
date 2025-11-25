FROM node:24-slim AS base

WORKDIR /usr/src/app

COPY ./package.json ./package-lock.json ./

FROM base AS builder

# copying package.json files to install dependnecies
COPY ./libs/ts/common/package.json ./libs/ts/common/
COPY ./libs/ts/contracts/package.json ./libs/ts/contracts/
COPY ./microservices/jobs/package.json ./microservices/jobs/

RUN npm ci -w common -w contracts -w jobs

# copying app and libs source code
COPY ./libs/ts/ ./libs/ts
COPY ./libs/proto ./libs/proto
COPY ./microservices/jobs ./microservices/jobs

# bulding libs and jobs app only
RUN npm run build -w common -w contracts -w jobs

FROM base AS dev

# copying node_modules from builder stage to decrease image size and speed up builds
COPY --from=builder /usr/src/app/node_modules/ ./node_modules

COPY --from=builder /usr/src/app/libs/ts/ ./libs/ts
COPY --from=builder /usr/src/app/libs/proto ./libs/proto
COPY --from=builder /usr/src/app/microservices/jobs ./microservices/jobs

WORKDIR /usr/src/app/microservices/jobs

CMD ["npx", "nest", "start", "--watch"]

FROM base AS prod

ENV NODE_ENV=production

COPY --from=builder /usr/src/app/microservices/jobs/healthcheck.js ./microservices/jobs/

COPY --from=builder /usr/src/app/microservices/jobs/package.json ./microservices/jobs/
COPY --from=builder /usr/src/app/microservices/jobs/dist ./microservices/jobs/dist/

COPY --from=builder /usr/src/app/libs/ts/common/package.json ./libs/ts/common/
COPY --from=builder /usr/src/app/libs/ts/common/dist  ./libs/ts/common/dist/

COPY --from=builder /usr/src/app/libs/ts/contracts/package.json ./libs/ts/contracts/
COPY --from=builder /usr/src/app/libs/ts/contracts/dist  ./libs/ts/contracts/dist/
COPY --from=builder /usr/src/app/libs/proto ./libs/proto

RUN npm ci --omit=dev -w common -w contracts -w jobs

USER node

WORKDIR /usr/src/app/microservices/jobs

CMD ["node", "./dist/src/main.js"]