from typing import Generic, TypeVar
T = TypeVar('T')

class Replay(Generic[T]):
  def __init__(self, iter):
    self._history = []
    self._iter = iter
  
  def __iter__(self):
    yield from self._history
    for item in self._iter:
      self._history.append(item)
      yield item
      #print(item)