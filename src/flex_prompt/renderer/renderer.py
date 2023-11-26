from abc import abstractmethod
from dataclasses import dataclass, replace
from ..cat import Cat
from typing import Generic, Iterable, TypeVar
from functools import cached_property, cache
from .context import Tokenizer, Context
from .rendering import Str

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

def names_from(fqn):
  if not fqn: return
  yield fqn
  _, _, tail = fqn.partition('.')
  yield from names_from(tail)

def fullname(cls):
  return f'{cls.__module__}.{cls.__qualname__}'
