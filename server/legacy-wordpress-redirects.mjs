// Historical WordPress query URLs verified from the migration inventory.
// Keep this list deliberately narrow: an unrecognised retired ID must not be
// sent to the home page, because that would be a soft-404 and obscure the
// original content intent from users and search engines.
export const portfolioTargets = Object.freeze({
  'classic-pokoj-dbl-twn': '/pl/pokoje/classic/',
  'pokoj-deluxe': '/pl/pokoje/deluxe/',
  'deluxe-premium-pokoj-dbl-twn': '/pl/pokoje/deluxe-premium/',
  'premium-pokoj': '/pl/pokoje/premium/',
  'suite-apartament': '/pl/pokoje/suite/',
  'deluxe-apartament': '/pl/pokoje/apartament-deluxe/',
  'prestige-apartament': '/pl/pokoje/prestige/',
  'prestige-deluxe-apartament': '/pl/pokoje/prestige-deluxe/',
  'hornigold-apartament': '/pl/pokoje/hornigold/'
});

export const pageTargets = Object.freeze({
  '7024': '/pl/rezerwacja/',
  '6903': '/pl/lokalizacja/',
  '6891': '/pl/sniadania/',
  '5885': '/pl/dokumenty/',
  '5884': '/pl/dokumenty/',
  '4231': '/en/contact/',
  '6624': '/en/',
  '24949:en': '/en/breakfast/',
  '24951:de': '/de/fruehstueck/',
  '24953:zh': '/zh-hans/%E6%97%A9%E9%A4%90/'
});

export const languageHomes = Object.freeze({pl: '/pl/', en: '/en/', de: '/de/', uk: '/uk/', es: '/es/', it: '/it/', zh: '/zh-hans/', 'zh-hans': '/zh-hans/', cs: '/cs/'});
const legacyKeys = new Set(['page_id', 'portfolio-item', 'lang']);

export function legacyWordpressRedirect(url) {
  const query = url.searchParams;
  if (![...legacyKeys].some(key => query.has(key))) return {kind: 'none'};

  const pageId = query.get('page_id');
  const language = (query.get('lang') || '').toLowerCase();
  const portfolio = query.get('portfolio-item');
  const path = portfolioTargets[portfolio]
    || pageTargets[pageId && language ? `${pageId}:${language}` : '']
    || pageTargets[pageId]
    || (!pageId && !portfolio ? languageHomes[language] : undefined);

  if (!path) return {kind: 'gone'};
  const target = new URL(path, url.origin);
  for (const [key, value] of query) if (!legacyKeys.has(key)) target.searchParams.append(key, value);
  return {kind: 'redirect', target};
}
