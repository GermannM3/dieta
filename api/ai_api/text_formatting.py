from pylatexenc.latex2text import LatexNodes2Text

async def style_changer(latex_code: str): 
    converter = LatexNodes2Text()
    latex_code = latex_code.replace('\\[', 'latex_zetta \\[')
    latex_code = latex_code.replace('\\]', '\\] latex_zetta')
    latex_code = latex_code.replace('\\(', 'latex_zetta \\(')
    latex_code = latex_code.replace('\\)', '\\) latex_zetta')
    text = converter.latex_to_text(latex_code)

    cleaned_text = ''
    null_rows = 0
    for row in text.splitlines():
        if row.strip() == '':
            null_rows += 1
            if null_rows == 1:
                cleaned_text += f'{row}\n'
        elif row.strip() != 'latex_zetta':
            null_rows = 0
            cleaned_text += f'{row}\n'
    

    cleaned_text = cleaned_text.replace('latex_zetta ', '')
    cleaned_text = cleaned_text.replace(' latex_zetta', '')
    cleaned_text = cleaned_text.replace('“', '```')
    cleaned_text = cleaned_text.replace('#####', '#')
    cleaned_text = cleaned_text.replace('####', '#')
    cleaned_text = cleaned_text.replace('###', '#')
    cleaned_text = cleaned_text.replace('##', '#')
    cleaned_text = cleaned_text.replace('**', '*')
    cleaned_text = cleaned_text.replace('````', '```')
    
    replacements = {
    '^2 ': '²',
    '^-2 ': '⁻²',
    '^3 ': '³',
    '^-3 ': '⁻³',
    '^n ': 'ⁿ',
    '^-n ': '⁻ⁿ',
    '^m ': 'ᵐ',
    '^-m ': '⁻ᵐ',
    '^+ ': '⁺',
    '^- ' : '⁻',
    '^4 ': '⁴',
    '^-4 ': '⁻⁴',
    '^5 ': '⁵',
    '^-5 ': '⁻⁵',
    '^6 ': '⁶',
    '^-6 ': '⁻⁶',
    '^7 ': '⁷',
    '^-7 ': '⁻⁷',
    '^8 ': '⁸',
    '^-8 ': '⁻⁸',
    '^i ': 'ⁱ',
    '^-i ': '⁻ⁱ',
    '^a ': 'ᵃ',
    '^-a ': '⁻ᵃ',
    }

    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    return cleaned_text