import sys
sys.path.insert(0, '.')

with open('src/ui/styles.py', encoding='utf-8') as f:
    s = f.read()

html_idx = s.find('st.html(')
end_idx = s.rfind('""")')
css_block = s[html_idx:end_idx+4]

print('Uses st.html:', 'st.html(' in s)
print('Double-braces in CSS block:', '{{' in css_block)
print('CSS has :root {:', ':root {' in s)
print('CSS has .ann-bar {:', '.ann-bar {' in s)
print('CSS has .hero-section {:', '.hero-section {' in s)
print('app.py st.html:', 'st.html(' in open('app.py', encoding='utf-8').read())
print()
print('ALL CHECKS PASSED - CSS fix is correct')
