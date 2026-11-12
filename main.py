import json
import math
import os

A = 1.6
B = 0.2
EPS = 0.22
N = 35
GAMMA = 0.003
SLOTS = 72
SHARE = [0.70, 0.70, 0.99, 0.99, 0.99, 0.90, 0.70, 0.80, 0.99, 0.70]


def weight(rank, place):
    w = 0.0
    for t in range(1, SLOTS + 1):
        sd = A + B * math.sqrt(t)
        decay = max(0.02, 1 - GAMMA * t)
        kernel = (1 - EPS) * math.exp(-0.5 * ((place - rank) / sd) ** 2) / sd + EPS / N
        w += decay * kernel
    return w


def main():
    in_dir = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    path = os.path.join(in_dir, 'history.ndjson')
    with open(path) as f:
        reads = [json.loads(l) for l in f if l.strip()]
    chart = reads[-1]['up_and_coming'] if reads else []
    chart = sorted(chart, key=lambda e: e['rank'])
    seen = set()
    cands = []
    for e in chart:
        u = int(e['universe_id'])
        if u in seen:
            continue
        seen.add(u)
        if e['rank'] <= N:
            cands.append((u, e['rank']))
    top10 = [u for u, _ in cands[:10]]

    rows = []
    for k in range(1, 11):
        ws = [(u, weight(r, k)) for u, r in cands]
        total = sum(w for _, w in ws)
        if total <= 0:
            continue
        for u, w in ws:
            p = SHARE[k - 1] * w / total
            if p < 5e-5:
                continue
            rows.append({'universe_id': u, 'place': k, 'p': p})

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'forecast.json'), 'w') as f:
        json.dump({'probabilities': rows, 'top10': top10}, f)


if __name__ == '__main__':
    main()
