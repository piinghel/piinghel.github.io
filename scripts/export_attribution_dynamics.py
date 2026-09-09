"""Export existing daily attribution for the article's time explorer.

No fit or portfolio replay. Supply --snapshot (frozen B3 folder) and --phases
(registered market-phase aggregates). Only aggregate factor series are public.
Requires Polars; verifies frozen inputs and daily/phase accounting identities.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import polars as pl

FACTORS = ['beta', 'volatility', 'momentum']
ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def export(snapshot, phases):
    folder = snapshot / 'factors'
    manifest = json.loads((folder / 'manifest.json').read_text())
    names = ['asset_factors.parquet', 'daily.parquet', 'factor_returns.parquet']
    for name in names:
        assert digest(folder / name) == manifest['output_sha256'][name], name
    phase_data = json.loads(phases.read_text())['episodes']
    bounds = [(dt.date.fromisoformat(e['peak']), dt.date.fromisoformat(e['strategy_trough'])) for e in phase_data]
    dates = pl.any_horizontal([pl.col('date').is_between(a, b, closed='right') for a, b in bounds])
    legs = (pl.scan_parquet(folder/'asset_factors.parquet')
            .filter(dates & pl.col('factor').is_in(FACTORS))
            .group_by('date', 'factor').agg(
                pl.col('signed_factor_exposure').filter(pl.col('view')=='long').sum().alias('long'),
                pl.col('signed_factor_exposure').filter(pl.col('view')=='short').sum().alias('short'),
                pl.col('pnl').sum().alias('asset_pnl'),
                pl.col('factor_return').first().alias('asset_factor_return'),
                pl.col('factor_return').n_unique().alias('return_count')))
    returns = (pl.scan_parquet(folder/'factor_returns.parquet').filter(dates)
               .select('date', *FACTORS).unpivot(index='date', variable_name='factor', value_name='return'))
    daily = (pl.scan_parquet(folder/'daily.parquet').filter(dates & pl.col('factor').is_in(FACTORS))
             .join(legs, on=['date','factor'], validate='1:1')
             .join(returns, on=['date','factor'], validate='1:1')
             .with_columns((pl.col('long')+pl.col('short')).alias('fitted_exposure'))
             .sort('date','factor').collect())
    assert daily.lazy().select((pl.col('return_count')==1).all()).collect().item()
    checks = daily.lazy().select(
        (pl.col('return')-pl.col('asset_factor_return')).abs().max().alias('factor_return'),
        (pl.col('pnl')-pl.col('asset_pnl')).abs().max().alias('pnl'),
        (pl.col('fitted_exposure')*pl.col('return')-pl.col('pnl')).abs().max().alias('product')
    ).collect().to_dicts()[0]
    assert all(v is not None and v < 1e-10 for v in checks.values()), checks
    output = {'source_hashes':{name:manifest['output_sha256'][name] for name in names},
              'phase_sha256':digest(phases), 'checks':checks, 'episodes':[]}
    for e, (start,end) in zip(phase_data,bounds):
        episode = {'label':e['peak'][:4]+'–'+e['strategy_trough'][2:4],
                   'low':e['market_low'],'peak':e['peak'],'end':e['strategy_trough'],'factors':{}}
        for factor in FACTORS:
            rows = daily.lazy().filter(pl.col('date').is_between(start,end,closed='right') & (pl.col('factor')==factor)).collect().to_dicts()
            assert len(rows)==e['decline']['sessions']+e['rebound']['sessions']
            for phase in ['decline','rebound']:
                lo,hi = e[phase]['start'],e[phase]['end']
                actual = sum(r['pnl'] for r in rows if lo<=str(r['date'])<=hi)*100
                expected = next(r['pnl_pp'] for r in e[phase]['fitted_factors'] if r['factor']==factor)
                assert abs(actual-expected)<1e-8, (factor,phase,actual,expected)
            cumulative_return=cumulative_pnl=0
            series=[]
            for r in rows:
                cumulative_return += 100*r['return']
                cumulative_pnl += 100*r['pnl']
                series.append([str(r['date']),r['long'],r['short'],r['fitted_exposure'],
                               100*r['return'],100*r['pnl'],cumulative_return,cumulative_pnl])
            episode['factors'][factor]=series
        output['episodes'].append(episode)
    target=ROOT/'assets/portfolio-attribution/dynamics.json'
    target.write_text(json.dumps(output,separators=(',',':'))+'\n')
    print(json.dumps({'daily_checks':checks,'output':str(target),'episodes':len(output['episodes'])}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    parser.add_argument('--phases',type=Path,required=True)
    args=parser.parse_args()
    export(args.snapshot,args.phases)
