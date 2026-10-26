var express = require('express'),
    { Pool } = require('pg'),
    cookieParser = require('cookie-parser'),
    path = require('path'),
    app = express(),
    server = require('http').Server(app),
    io = require('socket.io')(server);

var port = process.env.PORT || 4000;

io.on('connection', function (socket) {

  socket.emit('message', { text : 'Welcome!' });

  socket.on('subscribe', function (data) {
    socket.join(data.channel);
  });
});

// Separate fields preserve passwords containing URI delimiters.
var pool = new Pool({
  host: process.env.PGHOST || 'db',
  port: Number(process.env.PGPORT || 5432),
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  database: process.env.PGDATABASE || 'postgres',
  connectionTimeoutMillis: 2000,
  query_timeout: 2000,
  max: 3
});

app.get('/health/live', function (_req, res) { res.sendStatus(200); });
app.get('/health/ready', function (_req, res) {
  pool.query('SELECT 1 FROM votes LIMIT 1').then(function () { res.sendStatus(200); })
    .catch(function () { res.sendStatus(503); });
});

// Use short pool queries so a database restart cannot strand a checked-out client.
var stopping = false;
var voteTimer;
pool.on('error', function (error) {
  console.error('Database pool error:', error.code || 'unknown');
});
function getVotes() {
  pool.query('SELECT vote, COUNT(id) AS count FROM votes GROUP BY vote')
    .then(function (result) {
      io.sockets.emit('scores', JSON.stringify(collectVotesFromResult(result)));
    })
    .catch(function (error) { console.error('Waiting for votes database:', error.code || 'unknown'); })
    .finally(function () { if (!stopping) voteTimer = setTimeout(getVotes, 1000); });
}
getVotes();

function shutdown() {
  if (stopping) return;
  stopping = true;
  clearTimeout(voteTimer);
  var deadline = setTimeout(function () { process.exit(1); }, 10000);
  deadline.unref();
  io.close(function () {
    pool.end().then(function () { clearTimeout(deadline); process.exit(0); })
      .catch(function () { process.exit(1); });
  });
}
process.once('SIGTERM', shutdown);
process.once('SIGINT', shutdown);

function collectVotesFromResult(result) {
  var votes = {a: 0, b: 0};

  result.rows.forEach(function (row) {
    votes[row.vote] = parseInt(row.count);
  });

  return votes;
}

app.use(cookieParser());
app.use(express.urlencoded());
app.use(express.static(__dirname + '/views'));

app.get('/', function (req, res) {
  res.sendFile(path.resolve(__dirname + '/views/index.html'));
});

server.listen(port, function () {
  var port = server.address().port;
  console.log('App running on port ' + port);
});
