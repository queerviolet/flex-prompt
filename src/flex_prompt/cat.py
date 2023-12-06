from typing import Any, Iterable
from dataclasses import dataclass
from .context import Render, Overflow

@dataclass(init=False)
class Cat:
  children: tuple[Iterable[Any], ...]
  flex_weight: int = 1
  def __init__(self, *children: Iterable[Any], flex_weight=1, join: Any='', mode: str = 'block'):
    self.children = children
    self.flex_weight = flex_weight
    self.join = join
    self.mode = mode

  def __call__(self, render: Render) -> Iterable:
    rendered_join = render(self.join)
    join_len = 0
    first = True    
    for child in self.children:
      for item in child:
        output = render(item, token_limit=render.tokens_remaining - join_len)
        if self.mode == 'block' and output.overflow_token_count > 0:
          if output.overflow_token_count < render.token_limit:
            yield Overflow(output)
            return
        if join_len: yield rendered_join
        if first:
          join_len = len(rendered_join)
          first = False
        yield output
        if output.overflow_token_count: return
