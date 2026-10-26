FROM --platform=${BUILDPLATFORM} mcr.microsoft.com/dotnet/sdk:10.0-alpine@sha256:230c3fbae0ceedc70bca04eed2bfb5694e8b248cadbb81010f41b7a993601f55 AS build
WORKDIR /source
COPY Worker.csproj packages.lock.json ./
RUN dotnet restore --locked-mode
COPY Program.cs ./
RUN dotnet publish -c Release -o /app --self-contained false --no-restore

FROM mcr.microsoft.com/dotnet/runtime:10.0-alpine@sha256:e90a4b984926ed14328afec87e9be930b00dba55fed7e1743fbd585022afbad7 AS final
RUN addgroup -g 1000 capstone && adduser -D -u 1000 -G capstone capstone
WORKDIR /app
COPY --from=build --chown=capstone:capstone /app .
USER 1000:1000
ENTRYPOINT ["dotnet", "Worker.dll"]
