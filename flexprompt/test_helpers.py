
from flexprompt.renderer.renderer import StrRenderer

def infinite(s):
  while True:
    yield s

class CharTokenizer:
  def encode(self, input): return [*input]
  def decode(self, tokens): return ''.join(tokens)

render = StrRenderer(100, CharTokenizer())