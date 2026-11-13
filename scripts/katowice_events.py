"""Render the sourced Katowice calendar in the existing city guides."""
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import unquote
from silesia_holidays import ANCHOR, COPY as HOLIDAY_COPY, render_holidays

COPY = {
    'pl': ('Kalendarz wydarzeń w Katowicach', 'Nadchodzące w 2026', 'Zapowiedziane na 2027', 'Wybrane wydarzenia z 2026 roku', 'Sprawdź program', 'Terminy według organizatorów. Przed podróżą sprawdź program i dostępność biletów. Kalendarz obejmuje opublikowane terminy.', ['Koncert / festiwal', 'Sport', 'Esport', 'Targi', 'Kongres', 'Kultura', 'Konkurs']),
    'en': ('Katowice events calendar', 'Coming up in 2026', 'Announced for 2027', 'Selected past events in 2026', 'Event details', 'Dates come from organisers. Check the programme and ticket availability before travelling. The calendar covers published dates.', ['Concert / festival', 'Sport', 'Esports', 'Fair', 'Conference', 'Culture', 'Competition']),
    'de': ('Veranstaltungskalender für Kattowitz', 'Noch 2026', 'Für 2027 angekündigt', 'Ausgewählte vergangene Veranstaltungen 2026', 'Zum Programm', 'Termine laut Veranstaltern. Bitte prüfen Sie vor der Anreise Programm und Ticketverfügbarkeit. Der Kalender enthält veröffentlichte Termine.', ['Konzert / Festival', 'Sport', 'E-Sport', 'Messe', 'Kongress', 'Kultur', 'Wettbewerb']),
    'cs': ('Kalendář akcí v Katovicích', 'Nadcházející akce v roce 2026', 'Ohlášené akce na rok 2027', 'Vybrané uplynulé akce roku 2026', 'Program akce', 'Termíny vycházejí z oznámení pořadatelů. Před cestou ověřte program a dostupnost vstupenek. Kalendář zahrnuje zveřejněné termíny.', ['Koncert / festival', 'Sport', 'Esport', 'Veletrh', 'Konference', 'Kultura', 'Soutěž']),
    'zh-hans': ('卡托维兹活动日历', '2026 年即将举行', '2027 年已公布活动', '2026 年往期活动精选', '查看活动详情', '日期以主办方公布为准。出发前请查看节目安排及余票。日历仅列出已经公布日期的活动。', ['音乐会／节庆', '体育', '电竞', '展会', '会议', '文化', '比赛']),
    'uk': ('Календар подій у Катовіце', 'Майбутні події 2026 року', 'Анонси на 2027 рік', 'Вибрані минулі події 2026 року', 'Деталі події', 'Дати наведено за повідомленнями організаторів. Перед поїздкою перевірте програму й наявність квитків. У календарі лише оприлюднені дати.', ['Концерт / фестиваль', 'Спорт', 'Кіберспорт', 'Виставка', 'Конгрес', 'Культура', 'Конкурс']),
    'es': ('Calendario de eventos en Katowice', 'Próximos eventos de 2026', 'Eventos anunciados para 2027', 'Selección de eventos pasados de 2026', 'Programa del evento', 'Fechas publicadas por los organizadores. Consulta el programa y la disponibilidad de entradas antes de viajar. El calendario recoge fechas anunciadas.', ['Concierto / festival', 'Deporte', 'Deportes electrónicos', 'Feria', 'Congreso', 'Cultura', 'Concurso']),
    'it': ('Calendario degli eventi a Katowice', 'Prossimi eventi del 2026', 'Eventi annunciati per il 2027', 'Una selezione di eventi passati del 2026', 'Programma dell’evento', 'Date pubblicate dagli organizzatori. Prima di partire controlla il programma e la disponibilità dei biglietti. Il calendario riporta le date annunciate.', ['Concerto / festival', 'Sport', 'Esport', 'Fiera', 'Congresso', 'Cultura', 'Concorso']),
}
CATEGORIES = ('music', 'sport', 'esport', 'fair', 'conference', 'culture', 'contest')
GUIDE = 'katowice/wydarzenie'
LINK_FROM = {'', 'pobyt/wydarzenie', 'miasto-i-okolice'}


def guide_routes(root, routes):
    result = {}
    for route in routes.values():
        path = root / 'site' / unquote(route).strip('/') / 'index.html'
        if f'data-page-key="{GUIDE}"' in path.read_text():
            result[route.split('/')[1]] = route
    if result.keys() != COPY.keys():
        raise ValueError('Missing localized Katowice event guide')
    return result


def apply_calendar(soup, language, data, routes):
    if not soup.main or not soup.body or language not in routes:
        return
    key = soup.body.get('data-page-key')
    title, upcoming, next_year, past, source_label, note, labels = COPY[language]
    if key in LINK_FROM:
        link = soup.new_tag('a', href=routes[language] + '#katowice-events')
        link.string = title
        paragraph = soup.new_tag('p')
        paragraph.append(link)
        paragraph.append(' · ')
        seasonal = soup.new_tag('a', href=routes[language] + '#' + ANCHOR)
        seasonal.string = HOLIDAY_COPY[language][0]
        paragraph.append(seasonal)
        intro = soup.select_one('main .page-intro') or soup.select_one('main .hero-content')
        if intro:
            intro.append(paragraph)
        else:
            soup.main.append(paragraph)
        return
    if key != GUIDE:
        return
    section = soup.new_tag('section', id='katowice-events', attrs={'class': 'wrap'})
    heading = soup.new_tag('h2')
    heading.string = title
    section.append(heading)
    paragraph = soup.new_tag('p')
    paragraph.string = note + ' (' + data['checked'] + ')'
    section.append(paragraph)
    categories = dict(zip(CATEGORIES, labels))
    groups = {upcoming: [], next_year: [], past: []}
    today = datetime.now(ZoneInfo('Europe/Warsaw')).date().isoformat()
    for event in data['events']:
        if event['end'] < today:
            groups[past].append(event)
        elif event['start'].startswith('2027'):
            groups[next_year].append(event)
        else:
            groups[upcoming].append(event)
    groups[next_year].extend(data.get('announced', []))
    for label, events in groups.items():
        if not events:
            continue
        header = soup.new_tag('h3')
        header.string = label
        section.append(header)
        listing = soup.new_tag('ul')
        for event in events:
            item = soup.new_tag('li')
            for i, value in enumerate(dict.fromkeys((event['period'],) if 'period' in event else (event['start'], event['end']))):
                if i:
                    item.append(' – ')
                time = soup.new_tag('time', datetime=value)
                time.string = value
                item.append(time)
            if 'period' in event:
                pending = {
                    'pl': 'szczegółowy termin do potwierdzenia', 'en': 'exact dates to be confirmed',
                    'de': 'genaue Termine noch offen', 'cs': 'přesný termín bude upřesněn',
                    'zh-hans': '具体日期待定', 'uk': 'точні дати уточнюються',
                    'es': 'fechas exactas por confirmar', 'it': 'date esatte da confermare',
                }
                item.append(' · ' + pending[language])
            item.append(' · ')
            name = soup.new_tag('strong')
            name.string = event['name']
            item.append(name)
            item.append(' · ' + event['venue'] + ' · ' + categories[event['category']] + ' · ')
            link = soup.new_tag('a', href=event['url'], attrs={'rel': 'noopener noreferrer'})
            link.string = source_label
            link['aria-label'] = source_label + ' — ' + event['name']
            item.append(link)
            listing.append(item)
        section.append(listing)
    soup.main.insert(1, section)
    section.insert_before(render_holidays(soup, language))
