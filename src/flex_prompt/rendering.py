
from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Generic, TypeVar
from collections.abc import Callable, Iterable
from .renderer.context import Context, Part, Tokens, Overflow
from .cat import Cat

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
  
  def __len__(self): return len(self.tokens)

  @cached_property
  def overflow_token_count(self) -> int:
    return sum((overflow_token_count(part) for part in self), 0)

  @cached_property
  def _iter(self):
    return self.render(self.input)
  
  @cached_property
  def token_count(self) -> int:
    return sum((token_count(part) for part in self), 0)

  def __iter__(self):
    yield from self._parts
    for part in self._iter:
      self._parts.append(part)
      self.tokens_remaining -= token_count(part)
      yield part

  def __call__(self, input, token_limit=None):
    if token_limit is None:
      token_limit = self.tokens_remaining
    return self.__class__(self.ctx, input, token_limit)

  def render(self, input):
    match input:
      case None: return
      case Part(): yield input
      case str(): yield from self.render_str(input)
      case Callable(): yield from map(self, input(self))
      case Iterable(): yield from Cat(input)(self)
      case _:
        yield from self.render_str(str(input))

  def render_str(self, input):
    encoded = self.ctx.encode(input)
    include = Tokens(encoded[:self.tokens_remaining])
    overflow = Tokens(encoded[self.tokens_remaining:])
    yield include
    if overflow: yield Overflow(overflow)

class Str(Rendering[str]):
  @cached_property
  def output(self) -> str:
    return self.ctx.decode(self.tokens)