from renderer.renderer import StrRenderer
from . import Renderer
from renderable import Flex, Cat
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

def infinite(s):
  while True:
    yield s

class CharTokenizer:
  def encode(self, input): return [*input]
  def decode(self, tokens): return ''.join(tokens)
render = StrRenderer(100, CharTokenizer())

def test_flex():
  assert render(Flex([
    infinite('A'),
    infinite('B'),
    infinite('C'),
  ]), max_tokens=6).output == 'AABBCC'

  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ]), max_tokens=8).output == 'AABBBBCC'

def test_flex_separator():
  assert render(Flex([
    infinite('A'),
    Cat(infinite('B'), flex_weight=2),
    infinite('C'),
  ], separator='--'), max_tokens=12).output == 'AA--BBBB--CC'


def test_callable(snapshot):
  render = Renderer.for_model(OpenAI())
  def prompt(inst, tips, examples, output, input):
    return Flex([
      inst,
      Cat(tips),
      Cat(output),
      Cat(examples, flex_weight=2),
      f'Input:{input}',
      f'Output:'
    ], separator='\n\n')
  snapshot.assert_match(render(prompt(
    inst='Make a nice list',
    input='something else',
    tips=map(lambda tip: f'Tip {tip[0]}: {tip[1]}\n',
                 enumerate(infinite("Do the right thing"))),    
    examples=map(lambda ex: f'Example {ex[0]}:\n{ex[1]}',
                 enumerate(infinite('Input: something\nOutput:\n  - a\n  - b\n  - c\n\n'))),
    output='Return a markdown list'
    ), max_tokens=300).output)
