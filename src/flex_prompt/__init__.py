from .context import Render
from .cat import Cat
from .flex import Flex
from .target import Target, target, register_target_finder
from .rendering import Str

from . import targets

def render(input, model, **kwargs) -> Str:
  return target(model)(input, **kwargs)
