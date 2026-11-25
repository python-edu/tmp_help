from pathlib import Path
import re


def history_to_md(filename):
    source = Path(filename).expanduser()
    target = source.with_suffix('.md')

    if source == target:
        raise ValueError('Input file must not be a Markdown file')

    lines = source.read_text(encoding='utf-8').splitlines()

    result = []
    in_code = False

    for line in lines:
        heading = re.match(
            r'^(?:\s*(?:\d+/)?\d+: )?(#{1,6} .*)$', line
        )

        if heading:
            if in_code:
                result.extend(['```', ''])
                in_code = False

            result.extend([heading.group(1), ''])

        else:
            if not in_code:
                result.append('```python')
                in_code = True

            result.append(line)

    if in_code:
        result.append('```')

    target.write_text('\n'.join(result) + '\n', encoding='utf-8')
