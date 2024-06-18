defmodule WorkerTest do
  use ExUnit.Case
  doctest Worker

  test "greets the world" do
    assert Worker.hello() == :world
  end
end
