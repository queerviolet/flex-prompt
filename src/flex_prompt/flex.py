
from dataclasses import dataclass
from typing import Iterable, Any
from . import Render

@dataclass
class Flex:
  children: list[Any]
  flex_weight: int = 1
  separator: Any = None

  def __call__(self, render: Render) -> Iterable:
    tokens_remaining = render.tokens_remaining
    flex_total_weight = sum((flex_weight(c) for c in self.children))
    if self.separator:
      separator = render(self.separator)
      tokens_remaining -= separator.token_count * (len(self.children) - 1)
      first = True
    for child in self.children:
      if self.separator and not first:
        yield separator
      else:
        first = False
      weight = flex_weight(child)
      size = int(tokens_remaining * weight / flex_total_weight)
      output = render(child, token_limit=size)
      tokens_remaining -= output.token_count
      flex_total_weight -= weight
      if tokens_remaining >= 0: yield output
      else: return

def flex_weight(child):
  return getattr(child, 'flex_weight', 1)