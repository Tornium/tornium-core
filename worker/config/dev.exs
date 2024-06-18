import Config

config :worker, Worker.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "tornium_oban",
  stacktrace: true,
  show_sensitive_data_on_connection_error: true,
  pool_size: 10

config :logger, :console, format: "[$level] $message\n"
