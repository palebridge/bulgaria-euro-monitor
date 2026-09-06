"""Fetch constrained Eurostat JSON-stat series; preserve successful data on errors."""
import concurrent.futures
import datetime as dt
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
CONFIG = {
    'inflation_bg': ('Bulgaria · HICP inflation', 'Annual change, %', 'prc_hicp_minr', dict(freq='M', geo='BG', coicop18='TOTAL', unit='RCH_A', sinceTimePeriod='2025-01')),
    'inflation_ea': ('Euro area (21 countries) · HICP inflation', 'Annual change, %; fixed EA21 composition', 'prc_hicp_minr', dict(freq='M', geo='EA21', coicop18='TOTAL', unit='RCH_A', sinceTimePeriod='2025-01')),
    'food_bg': ('Bulgaria · Food and non-alcoholic beverages', 'Annual HICP change, %', 'prc_hicp_minr', dict(freq='M', geo='BG', coicop18='CP01', unit='RCH_A', sinceTimePeriod='2025-01')),
    'gdp_bg': ('Bulgaria · Real GDP growth', 'Year-on-year change, %; seasonally and calendar adjusted', 'namq_10_gdp', dict(freq='Q', geo='BG', na_item='B1GQ', unit='CLV_PCH_SM', s_adj='SCA', sinceTimePeriod='2025-Q1')),
    'jobs_bg': ('Bulgaria · Unemployment', 'Share of active population, %; total age group, seasonally adjusted', 'une_rt_m', dict(freq='M', geo='BG', age='TOTAL', sex='T', unit='PC_ACT', s_adj='SA', sinceTimePeriod='2025-01')),
}

def decode(data):
    ids, sizes = data['id'], data['size']
    assert ids[-1] == 'time' and all(n == 1 for n in sizes[:-1]), 'Unexpected or empty dimensions'
    values, flags = data.get('value', {}), data.get('status', {})
    def item(obj, i):
        return obj.get(str(i)) if isinstance(obj, dict) else obj[i] if i < len(obj) else None
    points = []
    for period, i in sorted(data['dimension']['time']['category']['index'].items()):
        value = item(values, i)
        if isinstance(value, (int, float)) and math.isfinite(value):
            points.append(dict(period=period, value=value, flag=item(flags, i) or ''))
    assert points, 'No observations returned'
    return points

def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    previous = {}
    for path in [ROOT/'dist/series.json', ROOT/'.cache/series.json']:
        if path.exists():
            for key, record in json.loads(path.read_text()).get('series', {}).items():
                if record.get('fetched', '') >= previous.get(key, {}).get('fetched', ''):
                    previous[key] = record
    def fetch(entry):
        key, (label, unit, dataset, params) = entry
        url = BASE + dataset + '?' + urllib.parse.urlencode(params)
        result = dict(previous.get(key, {}), label=label, unit=unit, url=url)
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Bulgaria-Euro-Monitor/1.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.load(response)
            result.update(points=decode(data), fetched=now, source_updated=data.get('updated'), error=None)
            print(key, result['points'][-1]['period'], result['points'][-1]['value'])
        except Exception as exc:
            result['error'] = str(exc)
            print('WARNING:', key, str(exc))
        return key, result
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        series = dict(pool.map(fetch, CONFIG.items()))
    payload = json.dumps(dict(attempted=now, series=series), indent=2) + '\n'
    for path in [ROOT/'dist/series.json', ROOT/'.cache/series.json']:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp')
        temp.write_text(payload)
        temp.replace(path)
    if not any(s.get('points') for s in series.values()):
        raise SystemExit('No usable official data: deployment halted')

if __name__ == '__main__':
    main()
