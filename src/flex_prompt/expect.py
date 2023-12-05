from dataclasses import dataclass
from typing import Any, Callable

from .context import Render, Part

@dataclass(frozen=True, slots=True)
class Expect:
  """Expect a response from the LLM."""

  output_parser: Callable[[str], Any] = str

  def __call__(self, ctx: Render):
    yield Expectation(ctx.tokens_remaining, self.output_parser)

@dataclass(frozen=True, slots=True)
class Expectation(Part):
  """An expected response"""
  token_count: int
  output_parser: Callable[[str], Any]

  @property
  def expected_token_count(self) -> int:
    return self.token_count
