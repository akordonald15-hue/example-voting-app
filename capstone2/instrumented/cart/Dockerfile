FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS dependencies
WORKDIR /build
# Missing lock intentionally fails. No unreviewed npm install during deployment.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts
FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53
WORKDIR /app
COPY --from=dependencies --chown=node:node /build/node_modules ./node_modules
COPY --chown=node:node server.js telemetry.js red.cjs ./
RUN rm -rf /usr/local/lib/node_modules /opt/yarn* && rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/yarn /usr/local/bin/yarnpkg
USER node
EXPOSE 8080
CMD ["node", "server.js"]
