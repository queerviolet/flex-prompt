from dataclasses import dataclass, replace
from typing import Any, Generic, TypeVar, Protocol, Callable
from .context import Tokenizer

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class Target(Generic[T]):
  max_tokens: int
  tokenizer: Tokenizer
  rendering_type: Callable[['Target', Any], T]

  def encode(self, str):
    return self.tokenizer.encode(str)
  
  def decode(self, encoded):
    return self.tokenizer.decode(encoded)
  
  def __call__(self, input, **context_args) -> T:
    if context_args:
      return replace(self, **context_args)(input)
    return self.rendering_type(self, input)
