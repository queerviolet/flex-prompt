from .. import Target, register_target_finder
from ..rendering import Str

class CharTokenizer:
  def encode(self, input): return [*input]
  def decode(self, tokens): return ''.join(tokens)

@register_target_finder
def testing_model(model):
  if model == 'test-len-str':
    return Target(100, tokenizer=CharTokenizer(), rendering_type=Str)
  
