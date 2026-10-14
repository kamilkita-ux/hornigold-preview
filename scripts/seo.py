"""Local build-time SEO. No network, commercial claims or deployment actions."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import datetime
import subprocess
import xml.etree.ElementTree as ET

ORIGIN = 'https://hornigold.pl'
LANGS = {'pl', 'en', 'de', 'zh-Hans', 'uk', 'es', 'it'}
PREVIEW_ROBOTS = 'noindex,nofollow,noarchive'

def single_locale_routes(root):
    """Only explicitly registered Polish articles may have a one-language cluster."""
    registry = root / 'content/editorial-articles.json'
    if not registry.is_file():
        return set()
    data = json.loads(registry.read_text())
    routes = data.get('singleLocaleRoutes', [])
    if not isinstance(routes, list) or any(not isinstance(route, str) for route in routes):
        raise ValueError('singleLocaleRoutes must be an explicit list of routes')
    articles = {row['route']: row for row in data.get('articles', [])}
    if len(routes) != len(set(routes)) or any(
        not route.startswith('/pl/artykuly/') or not route.endswith('/')
        or articles.get(route, {}).get('language') != 'pl' for route in routes
    ):
        raise ValueError('Single-locale routes must identify registered Polish articles')
    return set(routes)

def hreflang_languages(root, route):
    return ({'pl'} if route in single_locale_routes(root) else LANGS) | {'x-default'}

def source_date_utc(timestamp):
    """Use the actual Git instant, consistently across author and CI timezones."""
    value = datetime.datetime.fromisoformat(timestamp)
    if value.tzinfo is None:
        raise ValueError('Git timestamp must include its timezone')
    return value.astimezone(datetime.timezone.utc).date().isoformat()

def indexable_route(root, route):
    policy=json.loads((root/'seo/indexing-policy.json').read_text())
    return route not in policy['excludedRoutes']

def load_routes(root):
    routes = json.loads((root / 'routes.json').read_text())
    return {unquote(r): r for r in routes}

def route_for_file(path, directory):
    rel = path.relative_to(directory).as_posix()  # CloudMentor: na Windows str() daje "\" i żadna trasa nie pasuje
    return '/' + rel[:-10] if rel.endswith('index.html') else '/' + rel

def set_meta(soup, key, value, attr='name'):
    tags = soup.find_all('meta', attrs={attr: key})
    tag = tags[0] if tags else soup.new_tag('meta')
    for extra in tags[1:]: extra.decompose()
    tag[attr] = key
    tag['content'] = value
    if not tags: soup.head.append(tag)

def visible_image_objects(soup, root):
    """Describe existing visible assets; never infer creator or licensing rights."""
    objects = []
    seen = set()
    assets = (root / 'site' / 'assets').resolve()
    for img in soup.select('main img[src][alt]'):
        if any(parent.has_attr('hidden') or parent.get('aria-hidden') == 'true'
               for parent in [img, *img.parents] if getattr(parent, 'attrs', None)):
            continue
        src = urlsplit(img['src'])
        description = img['alt'].strip()
        if src.scheme or src.netloc or not src.path.startswith('/assets/') or not description:
            continue
        path = (root / 'site' / unquote(src.path).lstrip('/')).resolve()
        if not path.is_relative_to(assets) or not path.is_file() or src.path in seen:
            continue
        seen.add(src.path)
        content_url = ORIGIN + src.path
        objects.append({'@type': 'ImageObject', '@id': content_url + '#image',
                        'contentUrl': content_url, 'description': description})
    return objects

def apply_seo(soup, route, root, mode, routes, overrides):
    canonical_route = routes.get(unquote(route))
    eligible = bool(canonical_route and indexable_route(root, canonical_route))
    indexable = bool(eligible and mode == 'production-ready')
    set_meta(soup, 'robots', ('index,follow' if indexable else 'noindex,follow') if mode=='production-ready' and canonical_route else PREVIEW_ROBOTS)
    if mode=='production-ready' and canonical_route and not eligible:
        for alternate in soup.select('link[rel=alternate][hreflang]'): alternate.decompose()
    # Aliases and errors must not retain legacy business assertions.
    for script in soup.select('script[type="application/ld+json"]'): script.decompose()
    if not canonical_route:
        return
    url = ORIGIN + canonical_route
    if canonical_route in single_locale_routes(root):
        if soup.html.get('lang') != 'pl':
            raise ValueError('Registered Polish article has a different document language')
        for alternate in soup.select('link[rel=alternate][hreflang]'): alternate.decompose()
        for alternate in soup.select('meta[property="og:locale:alternate"]'): alternate.decompose()
        if mode == 'preview' or eligible:
            for language in ('pl', 'x-default'):
                soup.head.append(soup.new_tag('link', rel='alternate', hreflang=language, href=url))
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
    facts=json.loads((root/'content/verified-facts-2026-10-11.json').read_text())
    entity_id=ORIGIN+'/#lodging'
    graph={'@context':'https://schema.org','@graph':[
        {'@type':'WebPage','@id':url+'#page','url':url,'name':title,'description':description,'inLanguage':soup.html['lang'],'about':{'@id':entity_id}},
        {'@type':'LodgingBusiness','@id':entity_id,'name':facts['name'],'url':facts['url'],'address':facts['address']},
        {'@type':'Organization','@id':ORIGIN+'/#organization','name':facts['name'],'url':facts['url']}
    ]}
    socials=json.loads((root/'content/social-channels.json').read_text())
    same_as=[item['url'] for item in socials['links']]
    if same_as:
        graph['@graph'][1]['sameAs']=same_as
        graph['@graph'][2]['sameAs']=same_as
    images = visible_image_objects(soup, root)
    if images:
        graph['@graph'][0]['image'] = [{'@id': item['@id']} for item in images]
        graph['@graph'].extend(images)
    # Visible home/current trail, translated using the existing page heading.
    home='/' + canonical_route.split('/')[1] + '/'
    if canonical_route!=home and soup.main and not soup.select_one('.breadcrumb'):
        trail=soup.new_tag('nav',attrs={'class':'breadcrumb','aria-label':'Breadcrumb'})
        link=soup.new_tag('a',href=home);link.string='Hornigold';trail.append(link)
        trail.append(' / ')
        current=soup.new_tag('span',attrs={'aria-current':'page'});current.string=soup.h1.get_text(' ',strip=True);trail.append(current)
        soup.main.insert(0,trail)
    # Breadcrumbs are derived only from actual visible links, never guessed slugs.
    nav=soup.select_one('.breadcrumb, [aria-label="Breadcrumb"]')
    if nav:
        items=[]
        for link in nav.select('a[href]'):
            target=link['href']
            if target.startswith('/') and target in routes.values():
                items.append({'@type':'ListItem','position':len(items)+1,'name':link.get_text(' ',strip=True),'item':ORIGIN+target})
        if items:
            items.append({'@type':'ListItem','position':len(items)+1,'name':soup.h1.get_text(' ',strip=True),'item':url})
            graph['@graph'].append({'@type':'BreadcrumbList','@id':url+'#breadcrumbs','itemListElement':items})
    # Only FAQ visible on the FAQ page; exclude unreviewed operational claims.
    if soup.body.get('data-page-key')=='faq':
        questions=[]
        for detail in soup.select('main details'):
            summary=detail.find('summary'); answer=detail.find('p')
            if summary and answer and ('office@hornigold.pl' in answer.get_text() or 'Kopernika 6' in answer.get_text()):
                questions.append({'@type':'Question','name':summary.get_text(' ',strip=True),'acceptedAnswer':{'@type':'Answer','text':answer.get_text(' ',strip=True)}})
        if questions:graph['@graph'].append({'@type':'FAQPage','@id':url+'#faq','mainEntity':questions})
    # Editorial content identifies its publisher, without inventing a personal author.
    if soup.body.get('data-page-key','').startswith('katowice/') and soup.select_one('main a[href^="https://"]'):
        graph['@graph'].append({'@type':'Article','@id':url+'#article','headline':soup.h1.get_text(' ',strip=True),'inLanguage':soup.html['lang'],'mainEntityOfPage':{'@id':url+'#page'},'publisher':{'@id':ORIGIN+'/#organization'}})
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
        # Date comes from actual source-file history, never the build clock.
        history=subprocess.run(['git','-c','core.quotePath=false','log','--format=@%cI','--name-only','--','site'],cwd=Path(__file__).resolve().parent.parent,text=True,capture_output=True,check=True).stdout
        changed={};stamp=None
        for line in history.splitlines():
            if line.startswith('@'): stamp=source_date_utc(line[1:])
            elif line.startswith('site/') and stamp: changed.setdefault(line,stamp)
        for route in sorted(routes.values()):
            if not indexable_route(Path(__file__).resolve().parent.parent,route): continue
            node = ET.SubElement(sitemap, namespace+'url')
            ET.SubElement(node, namespace+'loc').text = ORIGIN+route
            stamp=changed.get('site'+unquote(route)+'index.html')
            if stamp: ET.SubElement(node, namespace+'lastmod').text=stamp
        ET.ElementTree(sitemap).write(out/'sitemap.xml', encoding='utf-8', xml_declaration=True)
        # Headers only belong to this isolated artifact; source/preview protections stay intact.
        (out/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n/llms.txt\n  Content-Type: text/plain; charset=utf-8\n/404.html\n  X-Robots-Tag: noindex\n/*/404.html\n  X-Robots-Tag: noindex\n/documents/*\n  X-Robots-Tag: noindex\n")
