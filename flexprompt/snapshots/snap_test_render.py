# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_callable 1'] = '''Make a nice list

Tip 0: Do the right thing
Tip 1: Do the right thing
Tip 2: Do the right thing
Tip 3: Do the right thing
Tip 4: Do the right thing
Tip 5: Do the right thing


Return a markdown list

Example 0:
Input: something
Output:
  - a
  - b
  - c

Example 1:
Input: something
Output:
  - a
  - b
  - c

Example 2:
Input: something
Output:
  - a
  - b
  - c

Example 3:
Input: something
Output:
  - a
  - b
  - c



Input:something else

Output:'''
