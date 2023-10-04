from typing import Self

class Bounds:
  def __init__(self, min=0, max=None):
    self.min = min
    self.max = max if max is not None and max >= min else None

  @property
  def has_fixed_size(self) -> bool:
    return self.min == self.max
  
  def fill(self, new_max) -> int:
    """Fill up to the specified maximum size."""
    if self.max is None:
      return self.__class__(self.min, new_max)
    return self.__class__(self.min, min(self.max, new_max))

  def __repr__(self): return f'Bounds(min={self.min}, max={self.max})'

  def __add__(self, other) -> Self:
    if self.max is not None and other.max is not None:
      max = self.max + other.max
    else:
      max = None
    return Bounds(self.min + other.min, max)

  def __eq__(self, other) -> bool:
    return self.min == other.min and self.max == other.max

setattr(Bounds, 'ZERO', Bounds(0, 0))
setattr(Bounds, 'UNKNOWN', Bounds())
