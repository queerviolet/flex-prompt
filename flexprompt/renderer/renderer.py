from abc import abstractmethod
from dataclasses import dataclass, replace
from ..cat import Cat
from typing import Generic, Iterable, TypeVar
from functools import cached_property, cache
from .context import Tokenizer, Context
from .rendering import StrPart, Str, Overflow

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class Renderer(Generic[T]):
  max_tokens: int
  tokenizer: Tokenizer
  output_type: type[T] = Str  

  @classmethod
  def register(Self, class_or_fqn):
    if not isinstance(class_or_fqn, str):
      return Self.register(fullname(class_or_fqn))
    registry = Self._registry()
    def register_finder(finder):
      for name in names_from(class_or_fqn):
        registry[name] = finder
      return finder
    return register_finder
  
  @staticmethod
  @cache
  def _registry(): return {}

  @classmethod
  def for_model(Self, llm):
    registry = Self._registry()
    if isinstance(llm, str):
      qualname, _, model_name = llm.partition(':')
      return registry[qualname](model_name)
    return registry[fullname(llm.__class__)](llm, Self)
  
  def child(self, **props):
    return replace(self, **props)
  
  def encode(self, str):
    return self.tokenizer.encode(str)
  
  def decode(self, encoded):
    return self.tokenizer.decode(encoded)
  
  def __call__(self, input, **context_args) -> T:
    if context_args:
      return self.child(**context_args)(input)
    return self.output_type(self, input)

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
      yield from Cat(input)(self)
    else:
      yield from self.render(str(input))
  
  @abstractmethod
  def collect(self, action, output=None): pass    

def names_from(fqn):
  if not fqn: return
  yield fqn
  _, _, tail = fqn.partition('.')
  yield from names_from(tail)

def fullname(cls):
  return f'{cls.__module__}.{cls.__qualname__}'


# class StrRenderer(Renderer[str]):
#   output_type = str

#   def collect(self, action=None, output=None):
#     if output is None:
#       output = ''
#     if action is None: return output
#     match action:
#       case str(s): output += s
#       case StrPart(content): output += content
#       case Rendering() as r: output += r.output
#     return output

# from langchain.schema import ChatMessage

# class ChatRenderer(Renderer[list[ChatMessage]]):
#   output_type = list[ChatMessage]
#   str_renderer = StrRenderer

#   def collect(self, action, output=None):
#     if output is None:
#       output = []
#     message = None
#     print(f'{action=}')
#     match action:
#       case StrPart(object=ChatMessage() as message): pass
#       case StrPart(object=dict(kwargs)):
#         message = ChatMessage(**kwargs)
#       case StrPart(content):
#         print(f'{content=}')
#         message = ChatMessage(role='user', content=content)
#     print(f'{message=}')
#     if message: output.append(message)
#     return output
  
#   def renderer_class(self, output_type):
#     if output_type == str:
#       return self.__class__.str_renderer_class
#     return super().renderer_class(output_type)

#   # TODO: fix message list rendering
#   #
#   # def renderable_for(self, obj):
#   #   match obj:
#   #     case str(msg): return Msg(msg)
#   #     case dict(kwargs): return Msg(kwargs)
#   #   return super().renderable_for(obj)

# Collect: TypeAlias = Callable[[Any, T], T]
