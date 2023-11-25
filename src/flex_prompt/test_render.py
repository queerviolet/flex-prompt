
from langchain import OpenAI
from flex_prompt import Renderer, Flex, Cat
from .test_helpers import infinite, render

def test_callable(snapshot):
  def prompt(inst, tips, examples, output, input):    
    return Flex([
      inst,
      tips,
      output,
      Cat(examples, flex_weight=2),
      f'Input: {input}',
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
    ), max_tokens=2000).output)


def test_recursive(snapshot):
  def items(ctx):
    yield 'hello'
    yield Cat([1, 2, 3])
    yield Flex([infinite('a'), infinite('b'), infinite('c')])
  snapshot.assert_match(render(items, max_tokens=100).output)