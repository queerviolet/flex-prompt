from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, abstractmethod

class Tokenizer(Protocol):
  def encode(self, input: str) -> list[Any]: pass
  def decode(self, encoded: list[Any]) -> str: pass

T = TypeVar('T')
class Context(Protocol, Generic[T]):
  max_tokens: int
  tokenizer: Tokenizer
  output_type: type[T]

  @abstractmethod
  def __call__(self, input) -> T: pass

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
  def __len__(self): return len(self.cropped)

  @property
  def overflow_token_count(self):
    return len(self.cropped)