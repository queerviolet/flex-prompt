from abc import abstractmethod
from renderable import Renderable

class Renderer:
  max_tokens: int

  species_by_class = {}  
  species_by_classname = {}
  @classmethod
  def register(Self, renderer_class):
    Self.species_by_class[renderer_class.model_class] = renderer_class
    Self.species_by_classname[str(renderer_class.model_class.__name__)] = renderer_class

  @classmethod
  def for_model(Self, llm):
    if isinstance(llm, str):
      species, _, model_name = llm.partition(':')
      return Self.species_by_classname[species].for_model_name(model_name)
    return Self.species_by_class[llm.__class__].for_model(llm)

  def with_max_tokens(self, max_tokens):
    return  self.__class__(max_tokens=max_tokens, tokenizer=self.tokenizer, **self.kwargs)
  
  def __init__(self, max_tokens, tokenizer, **kwargs):
    self.max_tokens = max_tokens
    self.tokenizer = tokenizer
    self.kwargs = kwargs

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

  def render(self, obj):
    renderable = self.renderable_for(obj)
    out = renderable.render(self)
    count = self.len(out)
    if count > self.max_tokens:
      print(f'{out=}')
      raise OutOfBoundsError({
        "message": "Item rendered too many tokens",
        "renderable": renderable,
        "max_tokens": self.max_tokens,
        "actual_tokens": count
      })
    return out#self.decode(self.encode(out)[:self.max_tokens])
  
  def renderable_for(self, obj):
    if isinstance(obj, Renderable): return obj
    if isinstance(obj, str): return StrRenderable(obj)
    if isinstance(obj, Iterable): return Cat(list(obj))
    return StrRenderable(str(obj))

class OutOfBoundsError(BaseException): pass

from langchain.llms import OpenAI
import tiktoken
from functools import cached_property

class OpenAIRenderer(Renderer):
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


Renderer.register(OpenAIRenderer)