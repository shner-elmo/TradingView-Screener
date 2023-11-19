from __future__ import annotations

import re

import pandas as pd


def test_readme_examples():
    with open('../README.md', 'r', encoding='utf8') as f:
        source = f.read()

    matches = re.findall(r'(?<=```python)(.*?)(?=```)', source, re.DOTALL)

    lines = []
    for match in matches:
        for line in match.splitlines():
            line = line.strip().lstrip('>>> ')
            lines.append(line)

    pd.options.display.max_rows = 10  # hard limit, even on small DFs

    code = '\n'.join(lines)
    print(code)

    assert '>>>' not in code, 'cleaning failed'

    # try executing the code, if any of the examples fail than so will this script
    exec(code)


if __name__ == '__main__':
    main()

# TODO: add this to CI/CD (with GH actions)
