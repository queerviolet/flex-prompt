
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
    # Budget for the joiner if we were given one
    if self.join:
      separator = render(self.join)
      tokens_remaining -= separator.token_count * (len(self.children) - 1)
  
    # The approach here sadly requires rendering children twice,
    # but guarantees both fairness and greediness: we will fill
    # all the available space and apportion it to our children
    # according to their flex_weight.

    # Render all our children with the full window, then sort them
    # by their rendered size (low to high).
    initial_render = []
    for i, child in enumerate(self.children):
      initial_render.append((i, child, render(child)))      
    initial_render.sort(key=lambda r: r[2].token_count)
    
    # Starting with the smallest item, get a final-size rendering
    # for all our children, re-rendering them if need be.
    #
    # We start with our smallest children because these are the
    # most likely to render fewer tokens than their allotment,
    # freeing up tokens to be divided amongst our larger children.
    flex_total_weight = sum((flex_weight(c) for c in self.children))
    final = [None] * len(initial_render)
    for i, child, rendering in initial_render:
      weight = flex_weight(child)
      allocation = int(tokens_remaining * weight / flex_total_weight)
      # If the child rendered more tokens than its allocation,
      # re-render it at its allotted size.
      if rendering.token_count > allocation:
        rendering = render(child, token_limit=allocation)    
      tokens_remaining -= rendering.token_count
      flex_total_weight -= weight
      final[i] = rendering
    
    # Yield all rendered children in their proper order, with
    # the separator (if specified)
    if self.join: first = True
    for rendered in final:
      if self.join:
        if not first: yield separator
        else: first = False
      yield rendered

def flex_weight(child):
  return getattr(child, 'flex_weight', 1)

from abc import abstractmethod
class Flexed:
  """Flexed is an abc which renders its content() in a Flex"""  
  def __call__(self, render: Render) -> Iterable:
    yield Flex(list(self.content(render)), join=self.flex_join)

  @property
  def flex_join(self): return None

  @abstractmethod
  def content(self, render: Render) -> Iterable: pass