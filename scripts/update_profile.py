"""Generate profile SVGs from live public GitHub data. Python standard library only."""
import collections
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import html
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import urllib.request
import urllib.error

USER = 'rogineceniza'
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
TODAY = dt.datetime.now(dt.timezone.utc).date()


def get(url):
    headers = {'User-Agent': 'rogineceniza-profile', 'Accept': 'application/vnd.github+json'}
    if url.startswith('https://api.github.com/') and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
        if response.status == 202:
            raise RuntimeError('GitHub statistics are still being computed')
        if response.status == 204:
            return []
        body = response.read().decode()
        return json.loads(body) if url.startswith('https://api.github.com/') else body


def text(x, y, value, size=14, color='#b9c5c8'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(str(value))}</text>'


def svg(name, width, height, title, subtitle, body):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>
<rect width="100%" height="100%" rx="16" fill="#172129"/>
<g font-family="Verdana,Arial,sans-serif">{text(24,34,title,19,'#e2d2bd')}{text(24,57,subtitle,11)}{body}
{text(24,height-14,'rogineceniza · updated '+str(TODAY)+' UTC',10,'#849b9e')}</g></svg>'''
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(content)


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tips = {}
        self.tip = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date'):
            self.cells[attrs['id']] = (attrs['data-date'], int(attrs['data-level']))
        if tag == 'tool-tip':
            self.tip = attrs.get('for')
    def handle_data(self, data):
        if self.tip:
            self.tips[self.tip] = self.tips.get(self.tip, '') + data
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip = None
    def days(self):
        result = []
        for key, (date, level) in self.cells.items():
            tip = self.tips.get(key, '').strip()
            match = re.match(r'([\d,]+) contributions?\b', tip)
            if match:
                count = int(match[1].replace(',', ''))
            elif tip.startswith('No contributions'):
                count = 0
            else:
                raise RuntimeError('Unrecognized contribution calendar markup')
            result.append((dt.date.fromisoformat(date), level, count))
        result.sort()
        if len(result) < 350:
            raise RuntimeError('Incomplete contribution calendar; retaining previous assets')
        return result


def main():
    repos = []
    page = 1
    while True:
        batch = get(f'https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(r for r in batch if not r['private'])
        if len(batch) < 100:
            break
        page += 1
    owned = [r for r in repos if not r['fork']]
    calendar = Calendar()
    calendar.feed(get(f'https://github.com/users/{USER}/contributions'))
    days = calendar.days()
    total = sum(day[2] for day in days)
    rows = [('Public repositories (including forks)', len(repos)),
            ('Public original repositories', len(owned)),
            ('Stars on public original repositories', sum(r['stargazers_count'] for r in owned)),
            ('Contributions in displayed calendar', total)]
    body = ''.join(text(24,95+i*34,label,12)+text(365,95+i*34,value,17,'#c5d6bf') for i,(label,value) in enumerate(rows))
    svg('github-stats.svg',440,255,'GitHub, lately',f'Calendar: {days[0][0]} to {days[-1][0]}',body)

    languages = collections.Counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for values in pool.map(lambda repo: get(repo['languages_url']), owned):
            languages.update(values)
    total_bytes = sum(languages.values())
    body = ''
    for i,(language,count) in enumerate(languages.most_common(5)):
        y = 83+i*29
        pct = count / total_bytes * 100
        body += text(24,y,language,12)+text(340,y,f'{pct:.1f}%',12)
        body += f'<rect x="150" y="{y-10}" width="{max(1,pct*1.7):.1f}" height="10" rx="4" fill="#8fa8a8"/>'
    if not languages:
        body = text(24,100,'No language data returned by GitHub.')
    svg('top-languages.svg',440,255,'Languages on the desk','By bytes · public original repositories · top 5',body)

    # Isometric buildings: chronological weeks, weekday rows. No decorative fake data.
    first = days[0][0]
    first -= dt.timedelta(days=(first.weekday()+1)%7)
    body = ''
    for date,level,count in days:
        week = (date-first).days//7
        row = (date.weekday()+1)%7
        x,y = 115+week*13-row*9,115+week*3+row*8
        height = 2 if count == 0 else min(65,6+math.log2(count+1)*10)
        top = ['#293a43','#59747b','#79999c','#a5b9ab','#d5c8a9'][level]
        body += f'<g><title>{date}: {count} contributions</title>'
        body += f'<polygon points="{x},{y} {x+6},{y+3} {x+6},{y-height+3} {x},{y-height}" fill="#344d58"/>'
        body += f'<polygon points="{x+6},{y+3} {x+12},{y} {x+12},{y-height} {x+6},{y-height+3}" fill="#536f76"/>'
        body += f'<polygon points="{x},{y-height} {x+6},{y-height-3} {x+12},{y-height} {x+6},{y-height+3}" fill="{top}"/></g>'
    svg('rainy-city.svg',900,380,'A little city under cloudy skies',f'{days[0][0]} to {days[-1][0]} · {total} contributions · one building per day',body)

    # GitHub code_frequency includes all contributors on default branches.
    weeks = collections.defaultdict(lambda: [0,0])
    covered = 0
    def frequency(repo):
        try:
            values = get(repo['url']+'/stats/code_frequency')
            if not isinstance(values, list):
                raise RuntimeError('No code frequency data')
            return values
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            print(f'Code frequency unavailable for {repo["name"]}: {type(exc).__name__}', flush=True)
            return None
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(frequency, owned))
    for values in results:
        if values is not None:
            covered += 1
            for timestamp,added,deleted in values:
                date = dt.datetime.fromtimestamp(timestamp,dt.timezone.utc).date()
                weeks[date][0] += added
                weeks[date][1] += abs(deleted)
    sunday = TODAY-dt.timedelta(days=(TODAY.weekday()+1)%7)
    dates = [sunday-dt.timedelta(weeks=i) for i in reversed(range(12))]
    maximum = max([n for date in dates for n in weeks[date]]+[1])
    body = text(24,81,'Green: added · rose: deleted · bar height uses a log scale',11)
    if any(values for values in results if values is not None):
        for i,date in enumerate(dates):
            x = 72+i*67
            for j,(value,color) in enumerate(zip(weeks[date],['#a5b9ab','#b78e94'])):
                h = math.log1p(value)/math.log1p(maximum)*132
                body += f'<rect x="{x+j*20}" y="{240-h}" width="17" height="{h}" rx="2" fill="{color}"><title>Week {date}: {value} lines {"added" if j==0 else "deleted"}</title></rect>'
                body += text(x+j*20,230-h,value,8)
            body += text(x-3,262,date.strftime('%m/%d'),10)
    else:
        body += text(24,145,'GitHub has not returned code-frequency data yet.',16)
        body += text(24,175,'No values have been invented. A later refresh will try again.',12)
    svg('code-activity.svg',900,310,'Code changes · last 12 weeks',f'{covered}/{len(owned)} public original repos available · all contributors · default branches',body)
    update_waka()


def update_waka():
    token = os.environ.get('WAKATIME_TOKEN')
    if os.environ.get('ENABLE_WAKATIME') != 'true' or not token:
        return
    # WakaTime stats reads require an OAuth bearer token, not the editor upload key.
    req = urllib.request.Request('https://wakatime.com/api/v1/users/current/stats/last_7_days',headers={'Authorization':'Bearer '+token})
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            data = json.load(response)['data']
        lines = ['Editor activity · last 7 days', '']
        lines.extend(f'{item["name"]}: {item["text"]} ({item["percent"]:.1f}%)' for item in data['languages'][:6])
        block = '\n```text\n'+'\n'.join(lines)+'\n```\n'
        path = ROOT/'README.md'
        content = path.read_text()
        content,n = re.subn(r'(?<=<!--START_SECTION:waka-->).*?(?=<!--END_SECTION:waka-->)',lambda _:block,content,flags=re.S)
        if n != 1:
            raise RuntimeError('Expected exactly one WakaTime marker pair')
        path.write_text(content)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        print('WakaTime unavailable; keeping the existing coding log.')


if __name__ == '__main__':
    main()
