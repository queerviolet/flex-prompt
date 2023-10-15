from typing_extensions import runtime_checkable
from typing import Protocol, Any, Iterable, Generic, TypeVar
from renderer.context import Context
from bounds import Bounds
from functools import cached_property
from renderer.context import Context

def flex_weight(child):
  return getattr(child, 'flex_weight', 1)

class Flex:
  def __init__(self, children, flex_weight=1):
    self.children = children
    self.flex_weight = flex_weight

  def bounds(self, ctx: Context) -> Bounds:
    return sum((child.bounds(ctx) for child in self.children(ctx)), Bounds.ZERO)
  
  def __call__(self, render: Context) -> Iterable:
    tokens_remaining = render.max_tokens
    flex_total_weight = sum((flex_weight(c) for c in self.children))

    for child in self.children:
      weight = flex_weight(child)
      size = int(tokens_remaining * weight / flex_total_weight)
      output = render(child, max_tokens=size)
      tokens_remaining -= output.token_count
      flex_total_weight -= weight
      if tokens_remaining >= 0: yield output
      else: return

class Cat:
  def __init__(self, iterable, flex_weight=1):
    self._iterable = iterable
    self.flex_weight = flex_weight

  def __call__(self, render: Context) -> Iterable:
    remaining = render.max_tokens
    for item in self._iterable:
      # print(f'Cat.render {child=}')
      rendered = render(item, max_tokens=remaining)
      # print(f'Cat.render {(rendered, rendered.token_count, remaining)=}')
      if rendered.overflow:
        return
      remaining -= rendered.token_count
      yield rendered
      if remaining <= 0: return   

from langchain.schema import ChatMessage

class Msg:
  def __init__(self, obj):
    self.obj = obj

  def __call__(self, ctx: Context):
    role = 'user'
    content = None
    name = None
    match self.obj:
      case str(content): pass
      case ChatMessage(role, content, name): pass
      case {'role': role, 'content': content, 'name': name}: pass
      case {'role': role, 'content': content}: pass
    rname = ctx.child(output_type=str).render(name)
    rrole = ctx.child(output_type=str).render(role)
    content_max = ctx.max_tokens - rname.token_count - rrole.token_count
    rcontent = ctx.child(output_type=str, max_tokens=content_max).render(content)
    msg = {'role': rrole.output, 'content': rcontent.output}
    if rname.output is not None:
      msg['name'] = rname.output
    token_count = 1 + rcontent.token_count + rrole.token_count
    yield ctx.obj(object=msg, token_count=token_count)
