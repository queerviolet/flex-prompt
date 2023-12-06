
from flex_prompt import Flex, Cat, Expect, render
from test_helpers import infinite

from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class MapInfinite:
  mapper: Callable
  s: Any
  def __iter__(self):
    yield from map(self.mapper, enumerate(infinite(self.s)))

def test_callable(snapshot):
  @dataclass
  class ComplexPrompt:
    inst: str
    tips: list[str]
    examples: list[str]
    input: str
    output: str | Expect = Expect
    def __call__(self, _ctx):
      yield Flex([
        self.inst,
        self.tips,
        self.output,
        Cat(self.examples, flex_weight=2),
        f'Input: {self.input}',
        f'Output:', Expect()
      ], join='\n\n')
  
  rendered = render(ComplexPrompt(
    inst='Make a nice list',
    input='something else',
    tips=MapInfinite(lambda tip: f'Tip {tip[0]}: {tip[1]}\n',
                     "Do the right thing"),
    examples=MapInfinite(lambda ex: f'Example {ex[0]}:\n{ex[1]}',
                         'Input: something\nOutput:\n  - a\n  - b\n  - c\n\n'),
    output='Return a markdown list'
    ), model='test-len-str', max_tokens=2000)
  snapshot.assert_match(rendered.output)
  assert rendered.expected_token_count == 504

def test_recursive(snapshot):
  def items(ctx):
    yield 'hello'
    yield Cat([1, 2, 3])
    yield Flex([infinite('a'), infinite('b'), infinite('c')])
  snapshot.assert_match(render(items, model='test-len-str', max_tokens=100).output)