FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS dependencies
WORKDIR /source
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts && npm cache clean --force

FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS development-dependencies
WORKDIR /source
COPY package.json package-lock.json ./
RUN npm ci --include=dev --ignore-scripts && npm cache clean --force

FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS final
# Node is PID 1; runtime needs no package manager or development watcher.
RUN apk add --no-cache zlib=1.3.2-r1 && rm -rf /usr/local/lib/node_modules /opt/yarn* &&     rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack /usr/local/bin/yarn /usr/local/bin/yarnpkg
WORKDIR /usr/local/app
COPY --from=dependencies --chown=node:node /source/node_modules /node_modules
COPY --chown=node:node server.js ./
COPY --chown=node:node views/ ./views/
ENV PORT=80
EXPOSE 80
USER node
CMD ["node", "server.js"]

# Last/default target preserves Compose's existing nodemon entrypoint and bind mount.
FROM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS dev
# Keep the local watcher; package managers are build-time tools, not runtime dependencies.
RUN apk add --no-cache curl tini brotli-libs=1.2.1-r0 && \
    rm -rf /usr/local/lib/node_modules /opt/yarn* && \
    rm -f /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack /usr/local/bin/yarn /usr/local/bin/yarnpkg
WORKDIR /usr/local/app
COPY --from=development-dependencies --chown=node:node /source/node_modules /node_modules
COPY --chown=node:node server.js ./
COPY --chown=node:node views/ ./views/
ENV PATH="/node_modules/.bin:$PATH" PORT=80
EXPOSE 80
USER node
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
