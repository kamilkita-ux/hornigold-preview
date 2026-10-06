"""Local build-time SEO. No network, commercial claims or deployment actions."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import xml.etree.ElementTree as ET

ORIGIN = 'https://hornigold.pl'
LANGS = {'pl', 'en', 'de', 'zh-Hans', 'uk', 'es', 'it'}
PREVIEW_ROBOTS = 'noindex,nofollow,noarchive'

def load_routes(root):
    routes = json.loads((root / 'routes.json').read_text())
    return {unquote(r): r for r in routes}

def route_for_file(path, directory):
    rel = str(path.relative_to(directory))
    return '/' + rel[:-10] if rel.endswith('index.html') else '/' + rel

def set_meta(soup, key, value, attr='name'):
    tags = soup.find_all('meta', attrs={attr: key})
    tag = tags[0] if tags else soup.new_tag('meta')
    for extra in tags[1:]: extra.decompose()
    tag[attr] = key
    tag['content'] = value
    if not tags: soup.head.append(tag)

def apply_seo(soup, route, root, mode, routes, overrides):
    canonical_route = routes.get(unquote(route))
    indexable = bool(canonical_route and mode == 'production-ready')
    set_meta(soup, 'robots', 'index,follow' if indexable else PREVIEW_ROBOTS)
    # Aliases and errors must not retain legacy business assertions.
    for script in soup.select('script[type="application/ld+json"]'): script.decompose()
    if not canonical_route:
        return
    url = ORIGIN + canonical_route
    override = overrides.get(canonical_route, {})
    if 'title' in override: soup.title.string = override['title']
    if 'description' in override: set_meta(soup, 'description', override['description'])
    title = soup.title.get_text(strip=True)
    description = soup.select_one('meta[name=description]')['content']
    for tag in soup.select('link[rel=canonical]'): tag.decompose()
    tag = soup.new_tag('link', rel='canonical', href=url); soup.head.append(tag)
    set_meta(soup, 'og:title', title, 'property')
    set_meta(soup, 'og:description', description, 'property')
    set_meta(soup, 'og:url', url, 'property')
    set_meta(soup, 'og:type', 'website', 'property')
    for name, value in [('twitter:card','summary_large_image'), ('twitter:title',title), ('twitter:description',description)]:
        set_meta(soup, name, value)
    image = soup.select_one('meta[property="og:image"]')
    if image:
        image['content'] = ORIGIN + urlsplit(image['content']).path
        set_meta(soup, 'twitter:image', image['content'])
        set_meta(soup, 'og:image:alt', title, 'property')
        set_meta(soup, 'twitter:image:alt', title)
    # Only page identity is asserted. Business claims require an explicit evidence dossier.
    graph = {'@context':'https://schema.org','@graph':[{
        '@type':'WebPage', '@id':url+'#page', 'url':url,
        'name':title, 'description':description, 'inLanguage':soup.html['lang']
    }]}
    script = soup.new_tag('script', type='application/ld+json')
    script.string = json.dumps(graph, ensure_ascii=False).replace('<', chr(92)+'u003c')
    soup.head.append(script)

def write_indexing_files(out, mode, routes):
    # A disallowed preview must not ship an indexable sitemap by accident.
    for file in out.glob('*sitemap*.xml'): file.unlink()
    if mode == 'preview':
        (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    else:
        (out/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+ORIGIN+'/sitemap.xml\n')
        ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        sitemap = ET.Element(namespace+'urlset')
        for route in sorted(routes.values()):
            node = ET.SubElement(sitemap, namespace+'url')
            ET.SubElement(node, namespace+'loc').text = ORIGIN+route
        ET.ElementTree(sitemap).write(out/'sitemap.xml', encoding='utf-8', xml_declaration=True)
        # Headers only belong to this isolated artifact; source/preview protections stay intact.
        (out/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n/llms.txt\n  Content-Type: text/plain; charset=utf-8\n/404.html\n  X-Robots-Tag: noindex\n/*/404.html\n  X-Robots-Tag: noindex\n/documents/*\n  X-Robots-Tag: noindex\n")
