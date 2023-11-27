from typing import Any, Iterable
from dataclasses import dataclass
from .renderer.context import Context, Overflow

@dataclass(init=False)
class Cat:
  children: list[Iterable[Any]]
  flex_weight: int = 1
  def __init__(self, *children: list[Iterable[Any]], flex_weight=1):
    self.children = children
    self.flex_weight = flex_weight

  def __call__(self, render: Context) -> Iterable:
    for child in self.children:
      for item in child:
        output = render(item)
        if output.overflow_token_count > 0:
          yield Overflow(output)
          return
        yield output
