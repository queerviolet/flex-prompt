from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

class Tokenizer(Protocol):
  def encode(self, input: str) -> list[Any]: pass
  def decode(self, encoded: list[Any]) -> str: pass

T = TypeVar('T', covariant=True)
class Render(Protocol[T]):
  @property
  def tokens_remaining(self) -> int: pass

  @property
  def token_limit(self) -> int: pass

  def __call__(self, input, token_limit=None) -> T: pass

class Part: pass

@dataclass(frozen=True, slots=True)
class Tokens(Part):
  tokens: list
  def __len__(self): return len(self.tokens)
  
  @property
  def token_count(self): return len(self.tokens)

@dataclass(frozen=True, slots=True)
class Overflow(Part):
  cropped: Part  
  def __len__(self):
    return len(self.cropped)

  @property
  def overflow_token_count(self):
    return len(self.cropped)