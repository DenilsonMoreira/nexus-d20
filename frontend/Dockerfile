FROM node:24-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./

FROM base AS development
RUN npm ci
COPY . .
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]

FROM base AS dependencies
RUN npm ci

FROM base AS builder
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:24-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
