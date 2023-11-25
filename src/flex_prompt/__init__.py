from .renderer import Renderer, Context
from .cat import Cat
from .flex import Flex

def render(input, model):
  return Renderer.for_model(model)(input)