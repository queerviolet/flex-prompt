from typing import Protocol, abstractmethod

class Context(Protocol):
  @abstractmethod
  def len(self, obj: str | list) -> int: pass
  max_tokens: int