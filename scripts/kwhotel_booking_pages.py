"""Jednorazowa podmiana bloków rezerwacji na podstronach (KWHotel/GuestSage, 2026-10-09). Idempotentny."""
from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parent.parent
HOTEL = 'c98ead00-c7fd-4013-bb45-f19539b932d4'
LANG = {'pl': 'pl', 'en': 'en', 'de': 'de', 'uk': 'uk', 'es': 'es', 'it': 'it', 'zh-hans': 'en'}
TEXT = {
 'pl': ('Zarezerwuj online', 'Dostępność, cenę i warunki zobaczysz w systemie rezerwacyjnym hotelu (KWHotel / GuestSage). Tam zakończysz rezerwację i płatność oraz zawrzesz umowę na warunkach hotelu.', 'Sprawdź dostępność i zarezerwuj', 'Dla grup powyżej 6 osób i zapytań firmowych skorzystaj z formularza zapytania poniżej.', 'Przycisk otwiera system rezerwacyjny hotelu w języku polskim.', 'Zobacz wszystkie dostępne pokoje'),
 'en': ('Book online', "You will see availability, rates and terms in the hotel's booking system (KWHotel / GuestSage). That is where you complete the booking and payment and conclude the contract on the hotel's terms.", 'Check availability and book', 'For groups of more than 6 people and business enquiries, use the enquiry form below.', "The button opens the hotel's booking system in English.", 'See all available rooms'),
 'de': ('Online buchen', 'Verfügbarkeit, Preise und Bedingungen sehen Sie im Buchungssystem des Hotels (KWHotel / GuestSage). Dort schließen Sie Buchung und Zahlung ab; der Vertrag kommt zu den Bedingungen des Hotels zustande.', 'Verfügbarkeit prüfen und buchen', 'Für Gruppen über 6 Personen und Firmenanfragen nutzen Sie bitte das Anfrageformular unten.', 'Die Schaltfläche öffnet das Buchungssystem des Hotels auf Deutsch.', 'Alle verfügbaren Zimmer ansehen'),
 'uk': ('Забронювати онлайн', 'Наявність, ціни та умови ви побачите в системі бронювання готелю (KWHotel / GuestSage). Там ви завершите бронювання й оплату та укладете договір на умовах готелю.', 'Перевірити наявність і забронювати', 'Для груп понад 6 осіб і корпоративних запитів скористайтеся формою запиту нижче.', 'Кнопка відкриває систему бронювання готелю українською мовою.', 'Переглянути всі доступні номери'),
 'es': ('Reserva en línea', 'Verás la disponibilidad, las tarifas y las condiciones en el sistema de reservas del hotel (KWHotel / GuestSage). Allí completarás la reserva y el pago y celebrarás el contrato según las condiciones del hotel.', 'Consultar disponibilidad y reservar', 'Para grupos de más de 6 personas y consultas de empresa, utiliza el formulario de consulta de abajo.', 'El botón abre el sistema de reservas del hotel en español.', 'Ver todas las habitaciones disponibles'),
 'it': ('Prenota online', "Disponibilità, prezzi e condizioni sono indicati nel sistema di prenotazione dell'hotel (KWHotel / GuestSage). Lì completerai prenotazione e pagamento e concluderai il contratto alle condizioni dell'hotel.", 'Verifica disponibilità e prenota', 'Per gruppi di oltre 6 persone e richieste aziendali, usa il modulo di richiesta qui sotto.', "Il pulsante apre il sistema di prenotazione dell'hotel in italiano.", 'Vedi tutte le camere disponibili'),
 'zh-hans': ('在线预订', '空房、价格和条款将在酒店预订系统（KWHotel / GuestSage）中显示。您将在该系统中完成预订和付款，并按酒店条款订立合同。', '查询空房并预订', '6人以上团体及企业咨询，请使用下方的咨询表单。', '预订系统暂无中文版本，按钮将以英文打开预订系统。', '查看所有可订房型'),
}
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
SCRIPT = '<script defer="" src="/assets/booking.js"></script>'
def one(pattern, repl, html, name):
    new, n = re.subn(pattern, lambda m: repl, html, count=1, flags=re.S)
    if n != 1: sys.exit(f'{name}: oczekiwano 1 dopasowania, jest {n}')
    return new
# Blok rezerwacji to stały panel, nie komunikat stanu: app.js:65 dopisuje „brak terminu” do pierwszego .notice.
OLD_PANEL, PANEL = '<div class="notice" role="status"><h2>', '<div class="booking-panel"><h2>'
BUTTON = r'<p><a class="button" data-booking=""[^>]*>[^<]*</a></p>'
for lang, engine in LANG.items():
    p = ROOT / 'site' / lang / 'rezerwacja' / 'index.html'
    html = p.read_text(encoding='utf-8')
    h2, lead, button, groups, limit, all_rooms = (esc(x) for x in TEXT[lang])
    # Ukryty odnośnik „wszystkie pokoje”: booking.js pokazuje go, gdy przycisk zawęża silnik do jednej kategorii.
    all_link = f'<p hidden=""><a class="text-link" data-booking-all="" href="https://be.guestsage.com/{engine}/{HOTEL}">{all_rooms}</a></p>'
    if 'data-booking=""' in html:  # nie samo 'data-booking': sekcja nagrody Kamila ma data-booking-award
        done = []
        if OLD_PANEL in html: html = html.replace(OLD_PANEL, PANEL, 1); done.append('panel')
        if 'data-booking-all=""' not in html:
            m = re.search(BUTTON, html)
            if not m: sys.exit(f'{lang}: brak przycisku rezerwacji')
            html = html[:m.end()] + all_link + html[m.end():]; done.append('wszystkie pokoje')
        if done: p.write_text(html, encoding='utf-8', newline='\n')
        print(lang, ', '.join(done) or 'już zmienione'); continue
    notice = (f'{PANEL}{h2}</h2><p>{lead}</p>'
              f'<p><a class="button" data-booking="" href="https://be.guestsage.com/{engine}/{HOTEL}">{button}</a></p>{all_link}'
              f'<p>{groups}</p></div>')
    html = one(r'<div class="notice" role="status">.*?</div>', notice, html, f'{lang} notice')
    html = one(r'<div class="integration-limit">.*?</div>', f'<div class="integration-limit"><p>{limit}</p></div>', html, f'{lang} limit')
    m = re.search(r'<script defer="" src="/assets/experience\.js[^"]*"></script>', html)
    if not m: sys.exit(f'{lang}: brak skryptu experience.js')
    html = html[:m.end()] + SCRIPT + html[m.end():]
    p.write_text(html, encoding='utf-8', newline='\n')
    print(lang, 'ok')

HELP = {
 'pl': 'Po wyborze pokoju rezerwację i płatność zakończysz w systemie rezerwacyjnym hotelu.',
 'en': "After choosing a room, you complete the booking and payment in the hotel's booking system.",
 'de': 'Nach der Zimmerwahl schließen Sie Buchung und Zahlung im Buchungssystem des Hotels ab.',
 'uk': 'Після вибору номера ви завершите бронювання й оплату в системі бронювання готелю.',
 'es': 'Tras elegir la habitación, completarás la reserva y el pago en el sistema de reservas del hotel.',
 'it': "Dopo aver scelto la camera, completerai prenotazione e pagamento nel sistema di prenotazione dell'hotel.",
 'zh-hans': '选定房型后，您将在酒店预订系统中完成预订和付款。',
}
for lang, text in HELP.items():
    for rel in (f'{lang}/index.html', f'{lang}/pobyt/index.html'):
        p = ROOT / 'site' / rel
        html = p.read_text(encoding='utf-8')
        html = one(r'<p class="form-help" id="date-help">.*?</p>', f'<p class="form-help" id="date-help">{esc(text)}</p>', html, rel)
        p.write_text(html, encoding='utf-8', newline='\n')
        print(rel, 'ok')

# Reguła .booking-panel na końcu style.css (CloudMentor 2026-10-09). Po konflikcie ze zmianą Kamila w style.css
# skrypt wydania bierze jego wersję i uruchamia ten skrypt — reguła wraca, jeśli jej brak.
CSS = ('/* CloudMentor 2026-10-09: panel rezerwacji GuestSage — wygląd jak .notice, bez roli komunikatu (app.js:65 pisze do .notice). */\n'
       '.booking-panel{padding:28px;background:var(--warm);border-left:3px solid var(--gold);margin-bottom:30px}.booking-panel h2{font-size:1.9rem}.booking-panel p:last-child{margin-bottom:0}@media(max-width:760px){.booking-panel{padding:22px}}\n')
p = ROOT / 'site' / 'assets' / 'style.css'
css = p.read_text(encoding='utf-8')
if '.booking-panel{' in css:
    print('style.css', 'już zmienione')
else:
    p.write_text(css + ('' if css.endswith('\n') else '\n') + CSS, encoding='utf-8', newline='\n')
    print('style.css', 'ok')
