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