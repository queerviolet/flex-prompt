from dataclasses import dataclass
from typing import Any

from .context import Render, Part

@dataclass(frozen=True, slots=True)
class Expect:
  """Expect a response from the LLM."""
  def __call__(self, ctx: Render):
    print("call expect")
    yield Expectation(ctx.tokens_remaining)

@dataclass(frozen=True, slots=True)
class Expectation(Part):
  """An expected response"""
  token_count: int
