"""Check generated image entities against source-visible, existing local assets."""
import argparse
import json
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
from seo import load_routes, visible_image_objects

ROOT = Path(__file__).resolve().parent.parent


def audit(directory):
    errors = []
    total = 0
    pages_with_images = 0
    routes = load_routes(ROOT)
    for route in routes.values():
        rel = unquote(route).lstrip('/') + 'index.html'
        source = BeautifulSoup((ROOT / 'site' / rel).read_text(), 'html.parser')
        built = BeautifulSoup((directory / rel).read_text(), 'html.parser')
        expected = visible_image_objects(source, ROOT)
        graph = json.loads(built.select_one('script[type="application/ld+json"]').string)['@graph']
        actual = [item for item in graph if item.get('@type') == 'ImageObject']
        page = next(item for item in graph if item.get('@type') == 'WebPage')
        references = [{'@id': item['@id']} for item in expected]
        if actual != expected or page.get('image', []) != references:
            errors.append({'route': route, 'rule': 'image entities and references match source-visible local files'})
        total += len(actual)
        pages_with_images += bool(actual)
    return {'routes': len(routes), 'pagesWithImages': pages_with_images,
            'imageEntities': total, 'errors': errors,
            'limits': ['No copyright, authorship, license or rich-result eligibility certification',
                       'No remote image or image rights claims are generated']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['preview', 'production-ready'], required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = audit(ROOT / ('_site' if args.mode == 'preview' else '_production_ready'))
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    assert json.loads(destination.read_text()) == result
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(bool(result['errors']))
