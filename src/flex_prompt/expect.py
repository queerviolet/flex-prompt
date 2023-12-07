from dataclasses import dataclass

from .context import Render, Part

@dataclass(frozen=True, slots=True)
class Expect:
  """Expect a response from the LLM."""
  flex_weight: int = 1

  def __call__(self, ctx: Render):
    yield Expectation(ctx.tokens_remaining)

@dataclass(frozen=True, slots=True)
class Expectation(Part):
  """An expected response"""
  token_count: int

  @property
  def expected_token_count(self) -> int:
    return self.token_count
