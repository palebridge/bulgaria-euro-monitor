"""Check deployable assets, source metadata, and nonempty official series."""
import json
from html.parser import HTMLParser
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / 'dist'
class Check(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href') and value and not value.startswith(('https:', 'http:', '#', 'data:')):
                assert (ROOT/value).is_file(), f'Missing asset {value}'
Check().feed((ROOT/'index.html').read_text())
snapshot = json.loads((ROOT/'snapshot.json').read_text())
assert len(snapshot['indicators']) == 8
for row in snapshot['indicators']:
    assert row['period'] and snapshot['sources'][row['source']]['url'].startswith('https://')
series = json.loads((ROOT/'series.json').read_text())['series']
for key, record in series.items():
    if record.get('points'):
        periods = [p['period'] for p in record['points']]
        assert periods == sorted(set(periods)), key
    else:
        assert record.get('error'), key
assert any(s.get('points') for s in series.values())
print('Validated assets, 8 sourced indicators and',len(series),'official series.')
