using System;
using System.Data.Common;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.IO;
using System.Runtime.InteropServices;
using Newtonsoft.Json;
using Npgsql;
using StackExchange.Redis;

namespace Worker
{
    public class Program
    {
        private static volatile bool stopping;
        public static int Main(string[] args)
        {
            using var terminate = PosixSignalRegistration.Create(PosixSignal.SIGTERM, context => {
                context.Cancel = true;
                stopping = true;
            });
            using var interrupt = PosixSignalRegistration.Create(PosixSignal.SIGINT, context => {
                context.Cancel = true;
                stopping = true;
            });
            try
            {
                var dbConfig = new NpgsqlConnectionStringBuilder {
                    Host = Environment.GetEnvironmentVariable("PGHOST") ?? "db",
                    Port = int.Parse(Environment.GetEnvironmentVariable("PGPORT") ?? "5432"),
                    Username = Environment.GetEnvironmentVariable("PGUSER") ?? "postgres",
                    Password = Environment.GetEnvironmentVariable("PGPASSWORD") ?? "postgres",
                    Database = Environment.GetEnvironmentVariable("PGDATABASE") ?? "postgres"
                };
                var connectionString = dbConfig.ConnectionString;
                var redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "redis";
                var heartbeatPath = Environment.GetEnvironmentVariable("WORKER_HEARTBEAT_PATH");
                long lastHeartbeat = 0;
                var pgsql = OpenDbConnection(connectionString);
                var redisConn = OpenRedisConnection(redisHost);
                var redis = redisConn.GetDatabase();

                // Keep alive is not implemented in Npgsql yet. This workaround was recommended:
                // https://github.com/npgsql/npgsql/issues/1214#issuecomment-235828359
                var keepAliveCommand = pgsql.CreateCommand();
                keepAliveCommand.CommandText = "SELECT 1";

                void ReconnectDatabase() {
                    keepAliveCommand.Dispose();
                    pgsql.Dispose();
                    pgsql = OpenDbConnection(connectionString);
                    keepAliveCommand = pgsql.CreateCommand();
                    keepAliveCommand.CommandText = "SELECT 1";
                }
                var definition = new { vote = "", voter_id = "" };
                while (!stopping)
                {
                    Thread.Sleep(100);
                    if (!redisConn.IsConnected) {
                        redisConn.Dispose();
                        redisConn = OpenRedisConnection(redisHost);
                        redis = redisConn.GetDatabase();
                    }
                    string json = redis.ListLeftPopAsync("votes").Result;
                    if (json != null) {
                        var vote = JsonConvert.DeserializeAnonymousType(json, definition);
                        // Keep this popped vote until its write succeeds or shutdown is requested.
                        bool written = false;
                        while (!written && !stopping) {
                            try {
                                if (pgsql.State != System.Data.ConnectionState.Open) ReconnectDatabase();
                                UpdateVote(pgsql, vote.voter_id, vote.vote);
                                written = true;
                            } catch (DbException) { ReconnectDatabase(); }
                        }
                    } else {
                        try { keepAliveCommand.ExecuteNonQuery(); }
                        catch (DbException) { ReconnectDatabase(); }
                    }
                    var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
                    if (!string.IsNullOrEmpty(heartbeatPath) && now - lastHeartbeat >= 5) {
                        File.WriteAllText(heartbeatPath, now.ToString());
                        lastHeartbeat = now;
                    }
                }
                keepAliveCommand.Dispose();
                pgsql.Dispose();
                redisConn.Dispose();
                return 0;
            }
            catch (OperationCanceledException) when (stopping) { return 0; }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex.ToString());
                return 1;
            }
        }

        private static NpgsqlConnection OpenDbConnection(string connectionString)
        {
            NpgsqlConnection connection = null;

            while (!stopping)
            {
                try
                {
                    connection = new NpgsqlConnection(connectionString);
                    connection.Open();
                    break;
                }
                catch (SocketException)
                {
                    Console.Error.WriteLine("Waiting for db");
                    Thread.Sleep(1000);
                }
                catch (DbException)
                {
                    Console.Error.WriteLine("Waiting for db");
                    Thread.Sleep(1000);
                }
            }

            if (stopping) throw new OperationCanceledException();
            Console.Error.WriteLine("Connected to db");

            var command = connection.CreateCommand();
            command.CommandText = @"CREATE TABLE IF NOT EXISTS votes (
                                        id VARCHAR(255) NOT NULL UNIQUE,
                                        vote VARCHAR(255) NOT NULL
                                    )";
            command.ExecuteNonQuery();

            return connection;
        }

        private static ConnectionMultiplexer OpenRedisConnection(string hostname)
        {
            // Use IP address to workaround https://github.com/StackExchange/StackExchange.Redis/issues/410
            var ipAddress = GetIp(hostname);
            Console.WriteLine($"Found redis at {ipAddress}");

            while (!stopping)
            {
                try
                {
                    Console.Error.WriteLine("Connecting to redis");
                    return ConnectionMultiplexer.Connect(ipAddress);
                }
                catch (RedisConnectionException)
                {
                    Console.Error.WriteLine("Waiting for redis");
                    Thread.Sleep(1000);
                }
            }
            throw new OperationCanceledException();
        }

        private static string GetIp(string hostname)
            => Dns.GetHostEntryAsync(hostname)
                .Result
                .AddressList
                .First(a => a.AddressFamily == AddressFamily.InterNetwork)
                .ToString();

        private static void UpdateVote(NpgsqlConnection connection, string voterId, string vote)
        {
            var command = connection.CreateCommand();
            try
            {
                command.CommandText = "INSERT INTO votes (id, vote) VALUES (@id, @vote)";
                command.Parameters.AddWithValue("@id", voterId);
                command.Parameters.AddWithValue("@vote", vote);
                command.ExecuteNonQuery();
            }
            catch (PostgresException error) when (error.SqlState == "23505")
            {
                command.CommandText = "UPDATE votes SET vote = @vote WHERE id = @id";
                command.ExecuteNonQuery();
            }
            finally
            {
                command.Dispose();
            }
        }
    }
}
