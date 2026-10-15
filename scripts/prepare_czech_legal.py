"""Prepare Czech legal source from reviewed paragraphs, without publishing."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / 'legal/en.json').read_text())
paragraphs = json.loads((ROOT / 'content/localization/cs-legal-reviewed.json').read_text())
titles = {
    'terms': 'Podmínky webu a právní informace',
    'booking': 'Rezervace, pobyt a reklamace',
    'payments': 'Pravidla plateb a vrácení peněz',
    'online-sales': 'Online rezervace a platby — informace pro hosty',
    'privacy': 'Zásady ochrany osobních údajů a informace podle GDPR',
    'cookies': 'Cookies, úložiště zařízení a vaše volby',
    'accessibility': 'Informace o přístupnosti',
    'safeguarding': 'Standardy ochrany dětí',
    'safeguarding-children': 'Vaše bezpečí — informace pro děti',
}
translations = {}
for section in source['sections']:
    key = section['id']
    assert len(section['paragraphs']) == len(paragraphs[key]), key
    translations[section['title']] = titles[key]
    translations.update(zip(section['paragraphs'], paragraphs[key]))
    section['title'] = titles[key]
    section['paragraphs'] = paragraphs[key]
source['title'] = 'Podmínky, soukromí a přístupnost'
source['intro'] = paragraphs['booking'][0]
source['download'] = 'Stáhnout všechny dokumenty ve formátu PDF'
ui = {
    'settings': 'Nastavení soukromí',
    'notice': 'Mapy Google, statistiky Google Analytics a měření reklam Google Ads jsou volitelné. Každá funkce vyžaduje samostatný souhlas a zůstává vypnutá, dokud jej neudělíte.',
    'necessary': 'Pouze nezbytné', 'save': 'Uložit volbu', 'close': 'Zavřít',
    'maps': 'Povolit mapy a panoramata Google',
    'mapDetail': 'Google obdrží mimo jiné vaši IP adresu, může používat vlastní cookies a zpracovávat údaje mimo EHP. Souhlas zde můžete kdykoli odvolat. Textové pokyny k příjezdu fungují i bez souhlasu.',
    'inactive': 'Statistiky fungují pouze na hornigold.pl po souhlasu; náhledy neodesílají analytické údaje.',
    'clear': 'Vymazat uložené volby a plán pobytu',
    'cleared': 'Údaje uložené tímto webem byly vymazány. Pro vyprázdnění formulářů také znovu načtěte stránku.',
    'privacyLink': 'Jak zpracováváme údaje',
    'form': 'Připravte poptávku místně a odešlete ji ze svého e-mailu. Marketingový souhlas není nutný. Přečtěte si, jak se vaše údaje zpracovávají.',
    'legal': 'Dokumenty a práva hostů', 'toc': 'Obsah dokumentů', 'quick': 'Rychlý přístup',
    'reviews': 'Hodnocení pochází z Googlu. Samostatně neověřujeme, zda u nás každý recenzent pobýval. Aktuální recenze a pravidla jejich zveřejňování najdete na Googlu.',
    'club': 'Výhody vyžadují potvrzení recepce a nejsou přiznány automaticky. Běžný pobyt lze sjednat bez členství nebo marketingového souhlasu. Samotná poptávka neznamená vstup do programu.',
    'analytics': 'Povolit statistiky Google Analytics',
    'analyticsDetail': 'Po souhlasu měří Google Analytics zobrazení stránek, zdroje návštěv a kliknutí na kontakty. Souhlas lze odvolat zde. Odmítnutí neomezuje obsah ani kontakt.',
    'documentVersion': 'Verze dokumentu', 'marketing': 'Povolit měření reklam Google Ads',
    'marketingDetail': 'Po samostatném souhlasu měří značka Google Ads AW-18507796156 účinnost reklam. Odmítnutí neomezuje tento web; souhlas lze odvolat zde. Personalizace reklam a měření nákupů nejsou zapnuté.',
}
old_ui = json.loads((ROOT / 'legal/en.json').read_text())['ui']
assert set(ui) == set(old_ui)
translations.update((old_ui[key], value) for key, value in ui.items())
source['ui'] = ui
source['sections'][6]['paragraphs'][2] = source['sections'][6]['paragraphs'][2].replace(
    'Připravovaná česká lokalizace rozšiřuje nabídku na osm jazyků;', 'Web nabízí osm jazyků;')
source['sections'][6]['paragraphs'][3] = source['sections'][6]['paragraphs'][3].replace('dokončený odběr', 'dokončené ověření')
source['sections'][6]['paragraphs'][4] = source['sections'][6]['paragraphs'][4].replace('Odběr musí', 'Ověření musí')
source['sections'][6]['paragraphs'][7] = source['sections'][6]['paragraphs'][7].replace('výsledky odběru', 'výsledky ověření')
(ROOT / 'legal/cs.json').write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n')
identity_file = ROOT / 'content/property-identity.json'
identities = json.loads(identity_file.read_text())
identity = dict(identities['en'])
identity.update(tagline='Hornigold je víc než hotel.',
    description='Hornigold w Zielonej Kamienicy nabízí 34 apartmánů k pronájmu v centru Katovic, na adrese ul. Mikołaja Kopernika 6.',
    rating='Hodnocení na Googlu: 4,6/5.',
    ratingNote='Zdroj načten 9. října 2026; hodnocení se může měnit. Google recenze neověřuje.',
    reviewLinkLabel='Přečíst hodnocení na Googlu')
identities['cs'] = identity
identity_file.write_text(json.dumps(identities, ensure_ascii=False, indent=2) + '\n')
queue = ROOT / 'content/localization/cs-translations.json'
rows = json.loads(queue.read_text())
for row in rows:
    if row['source'] in translations:
        row.update(translation=translations[row['source']], reviewed=True)
queue.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'legalSections': len(source['sections']), 'legalParagraphs': sum(len(s['paragraphs']) for s in source['sections']),
                  'reviewedStrings': sum(row['reviewed'] for row in rows), 'published': False}))
