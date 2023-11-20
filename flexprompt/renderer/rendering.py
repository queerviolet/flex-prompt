
from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Generic, TypeVar
from .context import Context

@dataclass
class StrPart:
  content: str
  token_count: int
  object: Any = None


@dataclass
class Overflow:
  cropped: str
  token_count: int

T = TypeVar('T')
class Rendering(Generic[T]):
  def __init__(self, ctx: Context, input):
    self.ctx = ctx
    self._history = []
    self._iter = ctx.render(input)

  @property  
  @abstractmethod
  def output(self) -> T: pass
  
  @cached_property
  def overflow(self) -> int:
    overflow = 0
    for part in self:
      match part:
        case Overflow(token_count=count): overflow += count
    return overflow
  
  @cached_property
  def token_count(self) -> int:
    count = 0
    for part in self:
      match part:
        case StrPart(token_count=int(token_count)): count += token_count
        case str(s): count += self.ctx.len(s)
        case _:  count += getattr(part, 'token_count', 0)
    return count

  def __iter__(self):
    yield from self._history
    for item in self._iter:
      self._history.append(item)
      yield item

from io import StringIO

class Str(Rendering[str]):
  @cached_property
  def output(self) -> str:
    output = StringIO()
    for part in self:
      match part:
        case str(s): output.write(s)
        case StrPart(content): output.write(content)
        case Rendering() as r: output.write(r.output)
    return output.getvalue()
