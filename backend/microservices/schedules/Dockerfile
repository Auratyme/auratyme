FROM node:24-slim AS base

WORKDIR /usr/src/app

COPY ./package.json ./package-lock.json ./

FROM base AS builder

# copying package.json files to install dependnecies
COPY ./libs/ts/common/package.json ./libs/ts/common/
COPY ./libs/ts/contracts/package.json ./libs/ts/contracts/
COPY ./microservices/schedules/package.json ./microservices/schedules/

RUN npm ci -w common -w contracts -w schedules

# copying app and libs source code
COPY ./libs/ts/ ./libs/ts
COPY ./libs/proto ./libs/proto
COPY ./microservices/schedules ./microservices/schedules

# bulding libs and schedules app only
RUN npm run build -w common -w contracts -w schedules

FROM base AS dev

# copying node_modules from builder stage to decrease image size and speed up builds
COPY --from=builder /usr/src/app/node_modules/ ./node_modules

COPY --from=builder /usr/src/app/libs/ts/ ./libs/ts
COPY --from=builder /usr/src/app/libs/proto ./libs/proto
COPY --from=builder /usr/src/app/microservices/schedules ./microservices/schedules

WORKDIR /usr/src/app/microservices/schedules

CMD ["npx", "nest", "start", "--watch"]

FROM base AS prod

ENV NODE_ENV=production

COPY --from=builder /usr/src/app/microservices/schedules/healthcheck.js ./microservices/schedules/

COPY --from=builder /usr/src/app/microservices/schedules/package.json ./microservices/schedules/
COPY --from=builder /usr/src/app/microservices/schedules/dist ./microservices/schedules/dist/

COPY --from=builder /usr/src/app/libs/ts/common/package.json ./libs/ts/common/
COPY --from=builder /usr/src/app/libs/ts/common/dist  ./libs/ts/common/dist/

COPY --from=builder /usr/src/app/libs/ts/contracts/package.json ./libs/ts/contracts/
COPY --from=builder /usr/src/app/libs/ts/contracts/dist  ./libs/ts/contracts/dist/
COPY --from=builder /usr/src/app/libs/proto ./libs/proto

RUN npm ci --omit=dev -w common -w contracts -w schedules

USER node

WORKDIR /usr/src/app/microservices/schedules

CMD ["node", "./dist/src/main.js"]