import re

with open('src/ui/styles.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'st.html("""\n'
end_marker = '\n""")'

start_idx = content.find(start_marker)
end_idx = content.rfind(end_marker)

if start_idx == -1 or end_idx == -1:
    print('ERROR: Could not find CSS block. start:', start_idx, 'end:', end_idx)
else:
    before = content[:start_idx + len(start_marker)]
    css_block = content[start_idx + len(start_marker):end_idx]
    after = content[end_idx:]

    count = css_block.count('{{')
    css_fixed = css_block.replace('{{', '{').replace('}}', '}')

    new_content = before + css_fixed + after
    with open('src/ui/styles.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'Fixed {count} double-brace pairs in CSS. Done.')
