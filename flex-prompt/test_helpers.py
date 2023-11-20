
from flexprompt.renderer.renderer import Renderer, Str

def infinite(s):
  while True:
    yield s

class CharTokenizer:
  def encode(self, input): return [*input]
  def decode(self, tokens): return ''.join(tokens)

render = Renderer(100, tokenizer=CharTokenizer(), output_type=Str)