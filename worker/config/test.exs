import Config

config :worker, Worker.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "tornium_oban#{System.get_env("MIX_TEST_PARTITION")}",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: System.schedulers_online() * 2

config :logger, level: :warning
