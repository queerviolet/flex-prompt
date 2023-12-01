from typing import Any, Iterable
from dataclasses import dataclass
from .context import Render, Overflow

@dataclass(init=False)
class Cat:
  children: tuple[Iterable[Any], ...]
  flex_weight: int = 1
  def __init__(self, *children: Iterable[Any], flex_weight=1):
    self.children = children
    self.flex_weight = flex_weight

  def __call__(self, render: Render) -> Iterable:
    for child in self.children:
      for item in child:
        output = render(item)
        if output.overflow_token_count > 0:
          yield Overflow(output)
          return
        yield output
