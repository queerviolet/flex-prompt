from typing import Any, Iterable
from dataclasses import dataclass
from .renderer.context import Context

@dataclass(init=False)
class Cat:
  children: list[Iterable[Any]]
  flex_weight: int = 1
  def __init__(self, *children: list[Iterable[Any]], flex_weight=1):
    self.children = children
    self.flex_weight = flex_weight

  def __call__(self, render: Context) -> Iterable:
    remaining = render.max_tokens
    for child in self.children:
      for item in child:
        # print(f'Cat.render {child=}')
        rendered = render(item, max_tokens=remaining)
        # print(f'Cat.render {(rendered, rendered.token_count, remaining)=}')
        if rendered.overflow:
          return
        remaining -= rendered.token_count
        yield rendered
        if remaining <= 0: return   

# from langchain.schema import ChatMessage

# class Msg:
#   def __init__(self, obj):
#     self.obj = obj

#   def __call__(self, ctx: Context):
#     role = 'user'
#     content = None
#     name = None
#     match self.obj:
#       case str(content): pass
#       case ChatMessage(role, content, name): pass
#       case {'role': role, 'content': content, 'name': name}: pass
#       case {'role': role, 'content': content}: pass
#     rname = ctx.child(output_type=str).render(name)
#     rrole = ctx.child(output_type=str).render(role)
#     content_max = ctx.max_tokens - rname.token_count - rrole.token_count
#     rcontent = ctx.child(output_type=str, max_tokens=content_max).render(content)
#     msg = {'role': rrole.output, 'content': rcontent.output}
#     if rname.output is not None:
#       msg['name'] = rname.output
#     token_count = 1 + rcontent.token_count + rrole.token_count
#     yield ctx.obj(object=msg, token_count=token_count)
