from typing import Generic, TypeVar, Any, Protocol, Type
from dataclasses import dataclass, replace

from .rendering import Rendering
from .find_target import target

T = TypeVar('T')
U = TypeVar('U')

class Renderer(Protocol[T]):
  def __call__(self, input, model, **kwargs) -> Rendering[T]: pass

@dataclass
class GenericRender(Renderer[Any]):
  output_type: Any = Any

  def __getitem__(self, output_type: type[U]) -> Renderer[U]:    
    return replace(self, output_type=output_type)

  def __call__(self, input, model, **kwargs) -> Rendering[Any]:
    return target(model)(input, **kwargs)    

render = GenericRender()
