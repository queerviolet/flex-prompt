from abc import abstractmethod
from dataclasses import dataclass
from ..cat import Cat
from typing import Callable, Generic, Iterable, TypeAlias, TypeVar, Protocol
from functools import cached_property
from .context import Context

T = TypeVar('T')
class Renderer(Generic[T]):
  max_tokens: int
  output_type: type[T]

  species_by_class = {}  
  species_by_classname = {}
  @classmethod
  def register(Self, renderer_class):
    Self.species_by_class[renderer_class.model_class] = renderer_class
    Self.species_by_classname[str(renderer_class.model_class.__name__)] = renderer_class
    return renderer_class

  @classmethod
  def for_model(Self, llm):
    if isinstance(llm, str):
      species, _, model_name = llm.partition(':')
      return Self.species_by_classname[species].for_model_name(model_name)
    return Self.species_by_class[llm.__class__].for_model(llm)

  def with_max_tokens(self, max_tokens):
    return self.__class__(max_tokens=max_tokens, tokenizer=self.tokenizer, **self.kwargs)
  
  def child(self, max_tokens=None, output_type=None, **kwargs):
    if max_tokens is None: max_tokens = self.max_tokens
    if output_type is None: output_type = self.output_type
    cls = self.renderer_class(output_type)
    return cls(max_tokens, tokenizer=self.tokenizer, **self.kwargs, **kwargs)
  
  def renderer_class(self, output_type):
    if output_type == self.output_type: return self.__class__
  
  def __init__(self, max_tokens: int, tokenizer, **kwargs):
    self.max_tokens = max_tokens
    self.tokenizer = tokenizer
    self.kwargs = kwargs

  def str(self, content):
    cropped = self.encode(content)[:self.max_tokens]
    token_count = len(cropped)
    return StrPart(content=self.decode(cropped), token_count=token_count)

  def obj(self, object, token_count):
    return StrPart(content='', token_count=token_count, object=object)

  @property
  def model_name(self):
    return self.kwargs.get('model_name', None)
  
  def encode(self, str):
    return self.tokenizer.encode(str)
  
  def decode(self, encoded):
    return self.tokenizer.decode(encoded)

  def len(self, obj):
    if isinstance(obj, str):
      return len(self.encode(obj))
    if isinstance(obj, list):
      return sum((self.len(o) for o in obj))
    raise TypeError('obj must be a string or list')
  
  def __call__(self, input, **context_args):
    if context_args:
      return self.child(**context_args)(input)
    return RenderPass(self, input)

  def render(self, input):
    if input is None: return
    if callable(input): yield from input(self)
    elif isinstance(input, str):
      encoded = self.encode(input)
      include = encoded[:self.max_tokens]
      yield StrPart(content=self.decode(include), token_count=len(include))
      overflow_count = len(encoded) - self.max_tokens
      if overflow_count > 0:
        yield Overflow(cropped=self.decode(encoded[self.max_tokens:]), token_count=overflow_count)
    elif isinstance(input, Iterable):
      yield from Cat(input) (self)
    else:
      yield str(input)
  
  @abstractmethod
  def collect(self, action, output=None): pass    

from typing import Any

@dataclass
class StrPart:
  content: str
  token_count: int
  object: Any = None


@dataclass
class Overflow:
  cropped: str
  token_count: int

class StrRenderer(Renderer[str]):
  output_type = str

  def collect(self, action=None, output=None):
    if output is None:
      output = ''
    if action is None: return output
    match action:
      case str(s): output += s
      case StrPart(content): output += content
      case RenderPass() as r: output += r.output
    return output

from langchain.schema import ChatMessage

class ChatRenderer(Renderer[list[ChatMessage]]):
  output_type = list[ChatMessage]
  str_renderer = StrRenderer

  def collect(self, action, output=None):
    if output is None:
      output = []
    message = None
    print(f'{action=}')
    match action:
      case StrPart(object=ChatMessage() as message): pass
      case StrPart(object=dict(kwargs)):
        message = ChatMessage(**kwargs)
      case StrPart(content):
        print(f'{content=}')
        message = ChatMessage(role='user', content=content)
    print(f'{message=}')
    if message: output.append(message)
    return output
  
  def renderer_class(self, output_type):
    if output_type == str:
      return self.__class__.str_renderer_class
    return super().renderer_class(output_type)

  # TODO: fix message list rendering
  #
  # def renderable_for(self, obj):
  #   match obj:
  #     case str(msg): return Msg(msg)
  #     case dict(kwargs): return Msg(kwargs)
  #   return super().renderable_for(obj)

Collect: TypeAlias = Callable[[Any, T], T]

class RenderPass(Generic[T]):
  def __init__(self, ctx: Context, input):
    self.ctx = ctx
    self._history = []
    self._iter = ctx.render(input)

  @cached_property
  def output(self) -> T:
    output = self.ctx.collect()
    for part in self:
      output = self.ctx.collect(part, output)
    return output
  
  @cached_property
  def overflow(self) -> int:
    overflow = 0
    for part in self:
      match part:
        case Overflow(token_count=count): overflow += count
    return overflow
  
  @cached_property
  def token_count(self) -> int:
    count = 0
    for part in self:
      match part:
        case StrPart(token_count=int(token_count)): count += token_count
        case str(s): count += self.ctx.len(s)
        case _:  count += getattr(part, 'token_count', 0)
    return count

  def __iter__(self):
    yield from self._history
    for item in self._iter:
      self._history.append(item)
      yield item
  

class OutOfBoundsError(BaseException): pass

from langchain.llms import OpenAI
import tiktoken
from functools import cached_property

@Renderer.register
class OpenAIRenderer(StrRenderer):
  model_class = OpenAI

  MAX_TOKENS = {
    'gpt-4': 8192,
    'gpt-4-0613': 8192,
    'gpt-4-32k': 32768,
    'gpt-4-32k-0613': 32768,
    'gpt-4-0314': 8192,
    'gpt-4-32k-0314': 32768,
    'gpt-3.5-turbo': 4097,
    'gpt-3.5-turbo-16k': 16385,
    'gpt-3.5-turbo-instruct': 4097,
    'gpt-3.5-turbo-0613': 4097,
    'gpt-3.5-turbo-16k-0613': 16385,
    'gpt-3.5-turbo-0301': 4097,
    'text-davinci-003': 4097,
    'text-davinci-002': 4097,
    'code-davinci-002': 8001,
    'babbage-002': 16384,
    'davinci-002': 16384,
    'text-curie-001': 2049,
    'text-babbage-001': 2049,
    'text-ada-001': 2049,
    'davinci': 2049,
    'curie': 2049,
    'babbage': 2049,
    'ada': 2049
  }

  @classmethod
  def for_model(Self, llm):
    return Self.for_model_name(llm.model_name)

  @classmethod
  def for_model_name(Self, model_name):
    return Self(model_name=model_name,
      tokenizer=tiktoken.encoding_for_model(model_name),
      max_tokens=Self.MAX_TOKENS[model_name])


from langchain.schema import ChatMessage
from langchain.chat_models import ChatOpenAI

@Renderer.register
class ChatOpenAIRenderer(ChatRenderer):
  model_class = ChatOpenAI
  str_renderer_class = OpenAIRenderer
  output_type = list[ChatMessage]

  @classmethod
  def for_model(Self, llm):
    return Self.for_model_name(llm.model_name)

  @classmethod
  def for_model_name(Self, model_name):
    return Self(model_name=model_name,
      tokenizer=tiktoken.encoding_for_model(model_name),
      max_tokens=OpenAIRenderer.MAX_TOKENS[model_name])  
