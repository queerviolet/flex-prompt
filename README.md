# flex[prompt]

**This readme is available as a [colab notebook](https://colab.research.google.com/drive/1AS_ra8v0OmC2UlnsWZghkRnLfmQXzpJ-?usp=sharing).**

Large language models have *maximum context window*—a maximum number of tokens they can receive and produce. You may have noticed this:

![Error message showing a model's maximum content length being exceeded](doc/screenshot-max-content-length.png)

Flex prompt addresses this by fitting your prompt into the model's context window. You provide a flexible prompt template, flex prompt renders it into model input.

Flex prompt does not handle model execution, but integrates well with execution frameworks like LangChain and Haystack.

# Basics

We'll install `flex-prompt` with the optional `openai` dependencies, since we're using OpenAI models for these examples. This will install `tiktoken`, the OpenAI tokenizer.

## Setup

```sh
pip install flex-prompt[openai]
```

Let's also get ourselves a long string to work with:

```python
#@title `WAR_AND_PEACE` = *(text of War and Peace from Project Gutenberg)*
WAR_AND_PEACE_URL = 'https://www.gutenberg.org/cache/epub/2600/pg2600.txt'
from urllib.request import urlopen
with urlopen(WAR_AND_PEACE_URL) as f: WAR_AND_PEACE = f.read().decode('utf-8')
```

Flex prompt is largely agnostic to how you run your models. We'll use LangChain for these examples.

```sh
pip install langchain openai
```

```python
from langchain.llms import OpenAI
```

# Quick Example


```python
from flex_prompt import render, Flex, Expect
from langchain.llms import OpenAI

# LangChain integration is optional; you can also call
# render with model=<model string> e.g. render(..., model='gpt-3.5-turbo')
davinci = OpenAI()

rendered = render(Flex([
  'Given the text, answer the question.\n',
  'Text:', WAR_AND_PEACE,
  'Question: Who wrote this?',
  'Answer:', Expect()
]), model=davinci)

print(davinci(rendered.output, max_tokens=rendered.max_response_tokens))
```

     Leo Tolstoy/Tolstoi


Here, we're using flex prompt's `Flex` component. `Flex` divides the available space in the prompt evenly amongst its children, filling the space completely. Neat!

But note that if we *entirely* fill the context window with our prompt, we'll have no more tokens left for the response! That's the role of `Expect`: it's a placeholder which participates in layout but doesn't render any tokens, leaving room for a response.

We can get the rendered prompt string from `rendered.output` and the number of tokens available for the response from `rendered.max_response_tokens`, which we use to call the model and get an answer.

## `flex_prompt.render`
Flex prompt exports a top-level `render` function which renders an input for a given model. This returns a `Rendering[str]`, whose `output` is the rendered prompt string.

The input can be as simple as a string:


```python
from flex_prompt import render
rendering = render("Q: What are the colors of the rainbow?\nA:", model='text-davinci-002')
rendering.output, rendering.max_response_tokens
```




    ('Q: What are the colors of the rainbow?\nA:', 4084)



The rendering has everything we need to call the model, here using LangChain:


```python
from langchain.llms import OpenAI
davinci = OpenAI(model='text-davinci-002')
davinci(rendering.output, max_tokens=rendering.max_response_tokens)
```




    ' Red, orange, yellow, green, blue, indigo, violet.'



For convenience, the `render` function also accepts LangChain models directly:




```python
rendering = render("Q: What are the colors of the rainbow?\nA:", model=davinci)
davinci(rendering.output, max_tokens=rendering.max_response_tokens)
```




    ' The colors of the rainbow are red, orange, yellow, green, blue, indigo, and violet.'



`render` will render most things you throw at it.

## strings

Rendered strings are cropped to fit. We can see this if we pass an artificially low `token_limit`:


```python
rendering = render("Q: What are the colors of the rainbow?\nA:", model=davinci, token_limit=5)
rendering.output
```




    'Q: What are the'



If the input overflowed, `overflow_token_count` will be non-zero:


```python
rendering.overflow_token_count
```




    8



(You can't do much with this information right now, except know that the prompt overflowed).

## lists

Rendering a `list` (or really, any non-`str` `Iterable`) concatenates all the items in that list:


```python
questions = ['1. Colors of the rainbow?\n', '2. Days of the week?\n']
rendering = render(['Answer the following questions:\n', questions], model=davinci)
rendering.output
```




    'Answer the following questions:\n1. Colors of the rainbow?\n2. Days of the week?\n'



By default, lists are rendered in `block` mode. This means that partial items which would be cut off simply aren't rendered at all:


```python
one = """
and lo betide, the red sky opened upon us as though the crinkled
hand of the heavens itself was reaching down.
"""
two = """
we were witness to dark and terrible portents, whose nameless
features we could not grasp with our mortal minds
"""
three = """
it was only then, in the moment when cruel stars had long since
wrung us dry, that the chinchillas arrived.
"""

rendering = render([one, two, three], model=davinci, token_limit=60)
print(rendering.output)
```

    
    and lo betide, the red sky opened upon us as though the crinkled
    hand of the heavens itself was reaching down.
    
    we were witness to dark and terrible portents, whose nameless
    features we could not grasp with our mortal minds
    


To control this, you can use the `Cat` component explicitly (list rendering uses `Cat` implicitly).

## components

If you hand render something which is callable, it will get called with a rendering context. This function must return an iterable over things which `render` can render.



```python
from flex_prompt import render, Expect

def ask_questions_text(text, question):
  yield 'Answer a question about this text:\n'
  yield text, '\n'
  yield 'Q: ', question, '\n'
  yield 'A: ', Expect()

rendering = render(ask_questions_text(text=[one, two, three], question='when did the chinchillas arrive?'), model=davinci)
print(rendering.output)
print(davinci(rendering.output, max_tokens=rendering.max_response_tokens))
```

    Answer a question about this text:
    
    and lo betide, the red sky opened upon us as though the crinkled
    hand of the heavens itself was reaching down.
    
    we were witness to dark and terrible portents, whose nameless
    features we could not grasp with our mortal minds
    
    it was only then, in the moment when cruel stars had long since
    wrung us dry, that the chinchillas arrived.
    
    Q: when did the chinchillas arrive?
    A: 
     The chinchillas arrived when the stars had long since wrung the mortals dry.


# Included components: `Flex` and `Cat`

Flex prompt includes two quite useful components: `Flex` and `Cat`

## `Flex`

`Flex` divides the available space amongst its children:


```python
from flex_prompt import render, Flex
A = 'A' * 10000
B = 'B' * 10000
C = 'C' * 10000
# the test-len-str model target is a test helper built into
# flex prompt. its tokenizer just returns each character as a token.
print(render(Flex([A, B, C]), model='test-len-str', token_limit=30).output)
```

    AAAAAAAAAABBBBBBBBBBCCCCCCCCCC


You can control how `Flex` divides the space with the `flex_weight` property, set on the child:


```python
for w in range(1, 5):
  rendering = render(
    Flex([A, Flex([B], flex_weight=w), C]),
    model='test-len-str',
    token_limit=30)
  print(rendering.output)
```

    AAAAAAAAAABBBBBBBBBBCCCCCCCCCC
    AAAAAAABBBBBBBBBBBBBBBCCCCCCCC
    AAAAAABBBBBBBBBBBBBBBBBBCCCCCC
    AAAAABBBBBBBBBBBBBBBBBBBBCCCCC


You can specify a `join` argument to make `Flex` join its children while respecting the window size:


```python
rendering = render(
  Flex([A, Flex([B], flex_weight=2), C], join='\n--\n'),
  model='test-len-str',
  token_limit=30)
print(rendering.output)
print('output length:', len(rendering.output))
```

    AAAAA
    --
    BBBBBBBBBBB
    --
    CCCCCC
    output length: 30


## `Cat`

Flex prompt's `Cat` component concatenates all the iterables you give it, and gives you more control over their rendering.

With no arguments, it's equivalent to rendering a list:


```python
from flex_prompt import render, Cat
rendering = render(Cat([one, two, three]), model=davinci, token_limit=40)
print(rendering.output)
```

    
    and lo betide, the red sky opened upon us as though the crinkled
    hand of the heavens itself was reaching down.
    


If you'd rather clip items which can't be completely rendered, you can specify `mode='clip'`:


```python
from flex_prompt import render, Cat
rendering = render(Cat([one, two, three], mode='clip'), model=davinci, token_limit=40)
print(rendering.output)
print(rendering.overflow_token_count, 'tokens clipped')
```

    
    and lo betide, the red sky opened upon us as though the crinkled
    hand of the heavens itself was reaching down.
    
    we were witness to dark and terrible portents,
    14 tokens clipped


`Cat` also lets you specify a `join`er, just as `Flex` does:


```python
from flex_prompt import render, Cat
rendering = render(Cat([one, two, three], mode='clip', join='---'), model=davinci, token_limit=70)
print(rendering.output)
```

    
    and lo betide, the red sky opened upon us as though the crinkled
    hand of the heavens itself was reaching down.
    ---
    we were witness to dark and terrible portents, whose nameless
    features we could not grasp with our mortal minds
    ---
    it was only then, in the moment when cruel stars had long


# Prompt components

`render` will accept almost any input. Relevantly, it will accept a callable generator, which it will then call with a rendering context. This lets us write prompt components—functional prompt templates describing not just string substitutions, but also basic layout instructions.

It's convenient to define prompt components as dataclasses:



```python
from flex_prompt import Flex, Cat, Render, Expect
from dataclasses import dataclass

@dataclass
class Ask:
  """Given a text, answer a question."""
  text: str
  question: str
  def __call__(self, ctx: Render):
    yield Flex([
      'Given the text, answer the question\n\n',
      'Text:\n', self.text, '\n',
      'Question: ', self.question,
      'Answer:', Expect()
    ])

rendered = render(Ask(text=WAR_AND_PEACE, question='Where is this text from?'), model=davinci)
davinci(rendered.output, max_tokens=rendered.expected_token_count)
```




    ' This text is from the Project Gutenberg eBook of War and Peace.'



# Targeting a particular model

When you call `render(input, model=m)`, flex prompt searches for a render `Target` for `m`. If you want to do this search once rather than every time you render, you can call `flex_prompt.target` to get a model-specific renderer:


```python
from flex_prompt import target, Flex, Expect
render = target(davinci)
rendering = render(Ask(text=WAR_AND_PEACE,
                       question='What might a 19th century Russian aristocrat think of this book?'))
print(davinci(rendering.output, max_tokens=rendering.expected_token_count))
```

     A 19th century Russian aristocrat would likely think highly of this book, as it was written by the famous Russian author Leo Tolstoy and is widely considered to be one of the greatest works of literature in history.


# Integrating new models

When you ask flex prompt to render against a model, it looks up a `Target` for that model by calling a series of target finders. You can register a target finder using `flex_prompt.register_target_finder`:


```python
from flex_prompt import register_target_finder, Target
from flex_prompt.rendering import Str
from typing import Any

class WordTokenizer:
  def encode(self, string):
    return list(self._encode(string))

  def decode(self, tokens):
    return ''.join(tokens)

  def _encode(self, string):
    import re
    start = 0
    for m in re.finditer(r'(\s|\n)+', string):
      space_start, space_end = m.span()
      word = string[start:space_start]
      if word: yield word
      yield string[space_start:space_end]
      start = space_end
    yield string[start:]

@register_target_finder
def find_example_target(model: Any) -> Target | None:
  if model == 'example-target':
    return Target(10, WordTokenizer(), Str)
```


```python
from flex_prompt import render
print(render(one, model='example-target').output)
```

    
    and lo betide, the red


# Known Issues

## Token accounting

Flex prompt operates in token space: when you hand it strings to render, it  tokenizes them and then concatenates those token lists. It only finally generates a string when you read the rendering's `.output` property (or convert it to a string, which implicitly does the same thing). Flex prompt's layout engine assumes that `token_count(A + B) = token_count(A) + token_count(B)`.

This makes layout a bit faster, since we avoid repeatedly calling the tokenizer as we concatenate substrings. Unfortunately, it's also incorrect.

Specifically, if adjacent prompt fragments combine into a single token, flex prompt will report a `token_count` which is higher than the actual token count. You can see this by combining individual-character substrings:


```python
from flex_prompt import target
render = target('gpt-4')

rendered = render([char for char in 'hello world']) # ['h', 'e', 'l', ...]
print('initial rendering token count:', rendered.token_count)
# rendered.output will be "hello world", so we're really just
# rendering a single string here:
print('actual token count:', render(rendered.output).token_count)
```

    initial rendering token count: 11
    actual token count: 2


Fortunately, this will always over-estimate the token count, so the fundamental guarantee that flex prompt fits prompts into the token window still holds. It is also *probably* a mistake to combine prompt sections in a way that could generate new words (that is, without whitespace), so this is unlikely to have a major impact in practice.

If an absolutely accurate accounting of tokens is important for your use case, you should re-count tokens as in the example above.
