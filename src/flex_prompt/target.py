from dataclasses import dataclass, fields, replace
from typing import Any, Generic, TypeVar, Callable
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
  
  def __call__(self, input, **kwargs) -> T:
    target_args = {
      (f.name): kwargs[f.name] for f in fields(Target) if f.name in kwargs
    }
    remaining_args = { arg: v for arg, v in kwargs.items() if arg not in target_args }
    if target_args:
      return replace(self, **target_args)(input, **remaining_args)
    return self.rendering_type(self, input, **kwargs)
