from typing_extensions import runtime_checkable
from typing import Protocol, Any, Iterable, Generic, TypeVar
from renderer.context import Context
from bounds import Bounds
from functools import cached_property
from renderer.context import Context

T = TypeVar('T')
@runtime_checkable
class Renderable(Protocol, Generic[T]):
  def render(self, ctx: Context) -> Iterable[T]: pass
  def bounds(self, ctx: Context) -> Bounds: return Bounds.UNKNOWN

  @property
  def flex_weight(self) -> int: return 1

class Str(Renderable[str]):
  def __init__(self, string):
    self._string = string

  def bounds(self, ctx: Context) -> Bounds:
    size = ctx.len(self._string)
    return Bounds(size, size)

  def render(self, ctx: Context) -> Iterable[str]:
    yield ctx.str(self._string)

  def __repr__(self):
    return f'Str(string={self._string})'

class Flex(Renderable[T]):
  def __init__(self, items):
    self.items = items

  def children(self, ctx: Context):
    for item in self.items:
      yield ctx.renderable_for(item)

  def bounds(self, ctx: Context) -> Bounds:
    return sum((child.bounds(ctx) for child in self.children(ctx)), Bounds.ZERO)

  def render(self, ctx: Context) -> Iterable[T]:
    token_budget = ctx.max_tokens
    total_weight = 0
    sized_renderables = []
    for renderable in self.children(ctx):
      bounds = renderable.bounds(ctx)
      sized_renderables.append((renderable, bounds.min))
      token_budget -= bounds.min
      if not bounds.has_fixed_size:
        # child participates in flexing. we'll portion out the
        # available tokens in a weighted average by flex_weight
        total_weight += getattr(renderable, 'flex_weight', 1)
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

      new_token_budget = token_budget - rendered.token_count + size
      # print(f'{new_token_budget=}')
      if new_token_budget < 0:
        break
      yield from rendered
      #yield from rendered
      # if isinstance(rendered, list):
      #   out.extend(rendered)
      # else:
      #   out.append(rendered)
      token_budget = new_token_budget

class Cat(Renderable):
  def __init__(self, iterable, flex_weight=1):
    self._iterable = iterable
    self._weight = flex_weight

  @property
  def flex_weight(self): return self._weight

  def render(self, ctx: Context) -> list:
    remaining = ctx.max_tokens
    for item in self._iterable:
      # print(f'Cat.render {child=}')
      rendered = ctx.with_max_tokens(remaining).render(item)
      # print(f'Cat.render {(rendered, rendered.token_count, remaining)=}')
      if rendered.token_count > remaining:
        return
      remaining -= rendered.token_count
      yield from rendered
      if remaining <= 0: return   

  def bounds(self, ctx: Context): return Bounds.UNKNOWN