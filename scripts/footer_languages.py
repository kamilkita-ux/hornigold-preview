"""Keep the visible footer inventory aligned with the release language order."""
LABELS = {'pl': 'PL', 'en': 'EN', 'cs': 'CS', 'de': 'DE',
          'zh-Hans': '中文', 'uk': 'УКР', 'es': 'ES', 'it': 'IT'}


def apply_footer_languages(soup, languages):
    inventory = ' / '.join(LABELS[language] for language in languages)
    for bottom in soup.select('footer .footer-bottom'):
        for span in bottom.find_all('span', recursive=False):
            if span.has_attr('data-language-inventory') or span.get_text(strip=True).startswith('PL / EN /'):
                span['data-language-inventory'] = ''
                span['translate'] = 'no'
                span.string = inventory
