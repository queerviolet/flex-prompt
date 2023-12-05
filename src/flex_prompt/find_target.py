
from dataclasses import dataclass, replace
from typing import Any, Protocol, TypeVar

from .target import Target
from .rendering import Rendering

T = TypeVar('T')
U = TypeVar('U')

class FindTarget(Protocol[T]):
  def __call__(self, model: Any) -> Target[Rendering[T]] | None: pass

@dataclass
class GenericFindTarget(FindTarget[Any]):
  output_type: Any = Any

  def __getitem__(self, output_type: type[U]) -> FindTarget[U]:
    return replace(self, output_type=output_type)

  def __call__(self, model) -> Target[Any]:
    for finder in _target_finders:
      target = finder(model)
      if target: return target
    raise KeyError(model)    

_target_finders = []
def register_target_finder(find: FindTarget[Any]):
  _target_finders.append(find)
  return find

target = GenericFindTarget()
