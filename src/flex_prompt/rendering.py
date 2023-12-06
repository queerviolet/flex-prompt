
from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Generic, TypeVar
from collections.abc import Callable, Iterable
from .context import Render, Part, Tokens, Overflow
from .cat import Cat
from .target import Target

def token_count(item):
  return getattr(item, 'token_count', 0)

def overflow_token_count(item):
  return getattr(item, 'overflow_token_count', 0)

def expected_token_count(item):
  return getattr(item, 'expected_token_count', 0)

T = TypeVar('T')
class Rendering(Generic[T], Part):
  def __init__(self, target: Target, input, token_limit = None):
    self.target = target
    self._parts: list[Part] = []
    self.input = input
    if token_limit is None:
      self.tokens_remaining = target.max_tokens
    else:
      self.tokens_remaining = token_limit
    self.token_limit = self.tokens_remaining    

  @property  
  @abstractmethod
  def output(self) -> T: pass

  @cached_property
  def tokens(self) -> list:
    tokens: list = []
    for part in self:
      tokens.extend(getattr(part, 'tokens', []))
    return tokens
  
  def __len__(self): return len(self.tokens)

  @cached_property
  def overflow_token_count(self) -> int:
    return sum((overflow_token_count(part) for part in self), 0)

  @cached_property
  def expected_token_count(self) -> int:
    return sum((expected_token_count(part) for part in self), 0)

  @cached_property
  def max_response_tokens(self) -> int:
    return self.expected_token_count

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
    return self.__class__(self.target, input, token_limit)

  def render(self, input):
    match input:
      case None: return
      case Part(): yield input
      case str(): yield from self.render_str(input)
      case Callable(): # type: ignore
        # https://github.com/python/mypy/issues/14014
        output = input(Context(self))
        if isinstance(output, str | Part) or not isinstance(output, Iterable):
          yield output
        else:
          yield from map(self, input(Context(self)))
      case Iterable(): yield from Cat(input)(Context(self))
      case _:
        yield from self.render_str(str(input))

  def render_str(self, input):
    encoded = self.target.encode(input)
    include = Tokens(encoded[:self.tokens_remaining])
    overflow = Tokens(encoded[self.tokens_remaining:])
    yield include
    if overflow: yield Overflow(overflow)

class Str(Rendering[str]):
  @cached_property
  def output(self) -> str:
    return self.target.decode(self.tokens)
  
  @cached_property
  def max_response_tokens(self) -> int:
    actual_count = len(self.target.encode(self.output))
    return self.token_limit - actual_count


R = TypeVar('R')
@dataclass(frozen=True, slots=True)
class Context(Generic[R], Render[Rendering[R]]):
  _rendering: Rendering[R]

  def __call__(self, input, token_limit=None) -> Rendering[R]:
    return self._rendering(input, token_limit=token_limit)
  
  @property
  def tokens_remaining(self):
    return self._rendering.tokens_remaining
  
  @property
  def token_limit(self):
    return self._rendering.token_limit