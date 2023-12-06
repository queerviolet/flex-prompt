
from dataclasses import dataclass
from typing import Iterable, Any
from . import Render

@dataclass
class Flex:
  children: list[Any]
  flex_weight: int = 1
  join: Any = None

  def __call__(self, render: Render) -> Iterable:
    tokens_remaining = render.tokens_remaining
    if self.join:
      separator = render(self.join)
      tokens_remaining -= separator.token_count * (len(self.children) - 1)
    initial_render = []
    for i, child in enumerate(self.children):
      initial_render.append((i, child, render(child)))      
    initial_render.sort(key=lambda r: r[2].token_count)
    
    flex_total_weight = sum((flex_weight(c) for c in self.children))
    final = [None] * len(initial_render)
    for i, child, rendering in initial_render:
      weight = flex_weight(child)
      allocation = int(tokens_remaining * weight / flex_total_weight)
      if rendering.token_count > allocation:
        rendering = render(child, token_limit=allocation)    
      tokens_remaining -= rendering.token_count
      flex_total_weight -= weight
      final[i] = rendering
    
    if self.join: first = True
    for rendered in final:
      if self.join:
        if not first: yield separator
        else: first = False
      yield rendered

def flex_weight(child):
  return getattr(child, 'flex_weight', 1)