from dataclasses import dataclass, replace
from typing import Generic, TypeVar
from .context import Tokenizer

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class Target(Generic[T]):
  max_tokens: int
  tokenizer: Tokenizer
  output_type: type[T]

  def encode(self, str):
    return self.tokenizer.encode(str)
  
  def decode(self, encoded):
    return self.tokenizer.decode(encoded)
  
  def __call__(self, input, **context_args) -> T:
    if context_args:
      return replace(self, **context_args)(input)
    return self.output_type(self, input)
