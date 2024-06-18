defmodule Worker.Repo.Migrations.AddObanJobsTable do
  use Ecto.Migration

  # See https://hexdocs.pm/oban/installation.html for more information

  def up do
    Oban.Migration.up(version: 12)
  end

  def down do
    Oban.Migration.down(version: 1)
  end
end
