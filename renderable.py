from typing_extensions import runtime_checkable
from typing import Protocol, Any, Iterable, Generic, TypeVar
from renderer.context import Context
from bounds import Bounds
from functools import cached_property
from renderer.context import Context

T = TypeVar('T')
@runtime_checkable
class Renderable(Protocol, Generic[T]):
  def render(self, ctx: Context) -> T: pass
  def bounds(self, ctx: Context) -> Bounds: return Bounds.UNKNOWN

  @property
  def flex_weight(self) -> int: return 1

class Renderable(Renderable[T]):
  @staticmethod
  def for_obj(obj):    
    if isinstance(obj, Renderable): return obj
    if isinstance(obj, str): return StrRenderable(obj)
    if isinstance(obj, Iterable): return Cat(list(obj))
    return StrRenderable(str(obj))

class StrRenderable(Renderable[str]):
  def __init__(self, string):
    self._string = string

  def bounds(self, ctx: Context) -> Bounds:
    size = ctx.len(self._string)
    return Bounds(size, size)

  def render(self, ctx: Context) -> str:
    return ctx.decode(ctx.encode(self._string)[:ctx.max_tokens])

  def __repr__(self):
    return f'StrRenderable(string={self._string})'

class Flex(Renderable[T]):
  def __init__(self, items):
    self._children = [Renderable.for_obj(o) for o in items]

  def bounds(self, ctx: Context) -> Bounds:
    return sum((child.bounds(ctx) for child in self._children), Bounds.ZERO)    

  def render(self, ctx: Context) -> list:
    token_budget = ctx.max_tokens
    total_weight = 0
    sized_renderables = []
    for renderable in self._children:
      bounds = renderable.bounds(ctx)
      sized_renderables.append((renderable, bounds.min))
      token_budget -= bounds.min
      if not bounds.has_fixed_size:
        # child participates in flexing. we'll portion out the
        # available tokens in a weighted average by flex_weight
        total_weight += getattr(renderable, 'flex_weight', 1)
    out = []
    for renderable, size in sized_renderables:
      # print(f'ListRenderable.render {(ctx.max_tokens, token_budget, renderable, size)=}')
      if not renderable.bounds(ctx).has_fixed_size:
        weight = getattr(renderable, 'flex_weight', 1)
        weighted_max = int(token_budget * weight / total_weight)
        max_tokens = renderable.bounds(ctx).fill(weighted_max).max
        rendered = ctx.with_max_tokens(max_tokens).render(renderable)
        # print(f'{(ctx.max_tokens, token_budget, max_tokens, rendered)=}')
        total_weight -= weight
      else:
        # print(f'{(ctx.max_tokens, token_budget, size, rendered)=}')
        rendered = ctx.with_max_tokens(size).render(renderable)
      # print(f'{rendered=}')
      # print(f'ListRenderable.render {(renderable, ctx.len(rendered))=}')
      # print(f'{token_budget=}')

      new_token_budget = token_budget - ctx.len(rendered) + size
      # print(f'{new_token_budget=}')
      if new_token_budget < 0:
        break
      if isinstance(rendered, list):
        out.extend(rendered)
      else:
        out.append(rendered)
      token_budget = new_token_budget
    return out

class Cat(Renderable):
  def __init__(self, iterable):
    self._iterable = iterable

  flex_weight = 1
  def render(self, ctx: Context) -> list:
    remaining = ctx.max_tokens
    out = []
    for item in self._iterable:
      child = Renderable.for_obj(item)
      # print(f'Cat.render {child=}')
      rendered = ctx.with_max_tokens(remaining).render(child)
      count = ctx.len(rendered)
      # print(f'Cat.render {(rendered, count, remaining)=}')
      if count > remaining:
        return out
      remaining -= count
      if isinstance(rendered, list):
        out.extend(rendered)
      else:
        out.append(rendered)
    return out

  def bounds(self, ctx: Context): return Bounds.UNKNOWN