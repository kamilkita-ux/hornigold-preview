"""Remove the legacy fixed date; the live counter supplies its own start date."""
def apply_counter_labels(soup, labels):
    language = soup.html.get('lang', 'pl').lower() if soup.html else 'pl'
    for paragraph in soup.select('footer .site-views'):
        count = paragraph.select_one('[data-view-count]')
        label = count.find_previous_sibling('span') if count else None
        if label is None:
            raise ValueError('Counter label missing')
        text = labels[language]
        label['data-view-label'] = ''
        label['data-neutral-label'] = text['neutral']
        label['data-since-label'] = text['since']
        label.string = text['neutral']
