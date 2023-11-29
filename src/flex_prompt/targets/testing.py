from ..target import Target, register_target_finder
from ..rendering import Str

class CharTokenizer:
  def encode(self, input): return [*input]
  def decode(self, tokens): return ''.join(tokens)

@register_target_finder
def testing_model(model, target: type[Target]):
  if model == 'test-len-str':
    return target(100, tokenizer=CharTokenizer(), output_type=Str)
  
