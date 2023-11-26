
from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Generic, TypeVar
from collections.abc import Callable, Iterable

from flex_prompt.cat import Cat
from .context import Context

@dataclass
class StrPart:
  content: str
  token_count: int

class Part: pass

@dataclass(frozen=True, slots=True)
class Tokens(Part):
  tokens: list
  overflow: list = None
  
  @property
  def token_count(self): return len(self.tokens)

  @property
  def overflow_token_count(self):
    return len(self.overflow) if self.overflow else 0

  def __len__(self): return len(self.tokens)

# @dataclass(frozen=True, slots=True)
# class Overflow(Part):
#   cropped: list
#   def __len__(self): return len(self.cropped)

def token_count(item):
  return getattr(item, 'token_count', 0)

def overflow_token_count(item):
  return getattr(item, 'overflow_token_count', 0)

T = TypeVar('T')
class Rendering(Generic[T], Part):
  def __init__(self, ctx: Context, input, token_limit = None):
    self.ctx = ctx
    self._parts = []
    self.input = input
    if token_limit is None:
      self.tokens_remaining = ctx.max_tokens
    else:
      self.tokens_remaining = token_limit

  @property  
  @abstractmethod
  def output(self) -> T: pass

  @cached_property
  def tokens(self) -> str:
    tokens = []
    for part in self:
      tokens.extend(getattr(part, 'tokens', []))
    return tokens

  @cached_property
  def overflow_token_count(self) -> int:
    return sum(overflow_token_count(part) for part in self)

  @cached_property
  def _iter(self):
    return self.render(self.input)
  
  @cached_property
  def token_count(self) -> int:
    return sum(token_count(part) for part in self)

  def __iter__(self):
    yield from self._parts
    for item in self._iter:
      for part in self.render(item):
        self._parts.append(part)
        self.tokens_remaining -= token_count(part)
        yield part

  def __call__(self, input, token_limit=None):
    if token_limit is None:
      token_limit = self.tokens_remaining
    return self.__class__(self.ctx, input, token_limit)

  def render(self, input):
    print(input, 'is part?', isinstance(input, Part))

    match input:
      case None: return
      case Part(): yield input
      case str(): yield from self.render_str(input)
      case Callable(): yield self(input(self))
      case Iterable(): yield from Cat(input)(self)      
      case _:
        yield from self.render_str(str(input))

  def render_str(self, input):
    encoded = self.ctx.encode(input)
    include = encoded[:self.tokens_remaining]
    overflow = encoded[self.tokens_remaining:]
    yield Tokens(include, overflow if overflow else None)


from io import StringIO

class Str(Rendering[str]):
  @cached_property
  def output(self) -> str:
    return self.ctx.decode(self.tokens)