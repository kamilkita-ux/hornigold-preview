"""Jednorazowa podmiana bloków rezerwacji na podstronach (KWHotel/GuestSage, 2026-10-09). Idempotentny."""
from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parent.parent
HOTEL = 'c98ead00-c7fd-4013-bb45-f19539b932d4'
LANG = {'pl': 'pl', 'en': 'en', 'de': 'de', 'uk': 'uk', 'es': 'es', 'it': 'it', 'zh-hans': 'en'}
TEXT = {
 'pl': ('Zarezerwuj online', 'Dostępność, cenę i warunki zobaczysz w systemie rezerwacyjnym hotelu (KWHotel / GuestSage). Tam zakończysz rezerwację i płatność oraz zawrzesz umowę na warunkach hotelu.', 'Sprawdź dostępność i zarezerwuj', 'Dla grup powyżej 6 osób i zapytań firmowych skorzystaj z formularza zapytania poniżej.', 'Przycisk otwiera system rezerwacyjny hotelu w języku polskim.'),
 'en': ('Book online', "You will see availability, rates and terms in the hotel's booking system (KWHotel / GuestSage). That is where you complete the booking and payment and conclude the contract on the hotel's terms.", 'Check availability and book', 'For groups of more than 6 people and business enquiries, use the enquiry form below.', "The button opens the hotel's booking system in English."),
 'de': ('Online buchen', 'Verfügbarkeit, Preise und Bedingungen sehen Sie im Buchungssystem des Hotels (KWHotel / GuestSage). Dort schließen Sie Buchung und Zahlung ab; der Vertrag kommt zu den Bedingungen des Hotels zustande.', 'Verfügbarkeit prüfen und buchen', 'Für Gruppen über 6 Personen und Firmenanfragen nutzen Sie bitte das Anfrageformular unten.', 'Die Schaltfläche öffnet das Buchungssystem des Hotels auf Deutsch.'),
 'uk': ('Забронювати онлайн', 'Наявність, ціни та умови ви побачите в системі бронювання готелю (KWHotel / GuestSage). Там ви завершите бронювання й оплату та укладете договір на умовах готелю.', 'Перевірити наявність і забронювати', 'Для груп понад 6 осіб і корпоративних запитів скористайтеся формою запиту нижче.', 'Кнопка відкриває систему бронювання готелю українською мовою.'),
 'es': ('Reserva en línea', 'Verás la disponibilidad, las tarifas y las condiciones en el sistema de reservas del hotel (KWHotel / GuestSage). Allí completarás la reserva y el pago y celebrarás el contrato según las condiciones del hotel.', 'Consultar disponibilidad y reservar', 'Para grupos de más de 6 personas y consultas de empresa, utiliza el formulario de consulta de abajo.', 'El botón abre el sistema de reservas del hotel en español.'),
 'it': ('Prenota online', "Disponibilità, prezzi e condizioni sono indicati nel sistema di prenotazione dell'hotel (KWHotel / GuestSage). Lì completerai prenotazione e pagamento e concluderai il contratto alle condizioni dell'hotel.", 'Verifica disponibilità e prenota', 'Per gruppi di oltre 6 persone e richieste aziendali, usa il modulo di richiesta qui sotto.', "Il pulsante apre il sistema di prenotazione dell'hotel in italiano."),
 'zh-hans': ('在线预订', '空房、价格和条款将在酒店预订系统（KWHotel / GuestSage）中显示。您将在该系统中完成预订和付款，并按酒店条款订立合同。', '查询空房并预订', '6人以上团体及企业咨询，请使用下方的咨询表单。', '预订系统暂无中文版本，按钮将以英文打开预订系统。'),
}
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
SCRIPT = '<script defer="" src="/assets/booking.js"></script>'
def one(pattern, repl, html, name):
    new, n = re.subn(pattern, lambda m: repl, html, count=1, flags=re.S)
    if n != 1: sys.exit(f'{name}: oczekiwano 1 dopasowania, jest {n}')
    return new
for lang, engine in LANG.items():
    p = ROOT / 'site' / lang / 'rezerwacja' / 'index.html'
    html = p.read_text(encoding='utf-8')
    if 'data-booking' in html: print(lang, 'już zmienione'); continue
    h2, lead, button, groups, limit = (esc(x) for x in TEXT[lang])
    notice = (f'<div class="notice" role="status"><h2>{h2}</h2><p>{lead}</p>'
              f'<p><a class="button" data-booking="" href="https://be.guestsage.com/{engine}/{HOTEL}">{button}</a></p>'
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
