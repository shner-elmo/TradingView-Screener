from __future__ import annotations

import re
import tradingview_screener
from pathlib import Path

import pandas as pd


def _test_readme_examples():
    readme = Path(tradingview_screener.__file__).parents[2] / 'README.md'
    source = readme.read_text(encoding='utf-8')

    matches = re.findall(r'(?<=```python)(.*?)(?=```)', source, re.DOTALL)

    lines = []
    for match in matches:
        for line in match.splitlines():
            line = line.lstrip('>>> ')
            lines.append(line)

    pd.options.display.max_rows = 10  # hard limit, even on small DFs

    code = '\n'.join(lines)
    print(code)

    assert '>>>' not in code, 'cleaning failed'

    # try executing the code, if any of the examples fail than so will this script
    exec(code)


if __name__ == '__main__':
    _test_readme_examples()

# TODO: add this to CI/CD (with GH actions)
