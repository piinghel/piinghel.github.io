"""Render all 11 primary recovery windows from published aggregate inputs."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT=Path(__file__).resolve().parents[1]/'assets/portfolio-attribution'

def render(rows,dark,mobile,horizon):
    c={'bg':'#171d24' if dark else '#ffffff','text':'#e4eaf0' if dark else '#263747',
       'grid':'#43505f' if dark else '#d6dfe5','long':'#57bdab' if dark else '#268b7b',
       'short':'#e69482' if dark else '#bd6559','net':'#8bb6ee' if dark else '#3a689c'}
    with plt.rc_context({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
                         'svg.fonttype':'none','svg.hashsalt':'recovery-comparison'}):
        fig,axes=plt.subplots(2 if mobile else 1,1 if mobile else 2,
                             figsize=(4.2,10.7) if mobile else (9.4,5.8),
                             gridspec_kw={} if mobile else {'width_ratios':[1.4,1]})
        fig.set_facecolor(c['bg'])
        for ax in axes:
            ax.set_facecolor(c['bg']);ax.spines[:].set_visible(False)
            ax.set_ylim(10.6,-.6)
            ax.set_yticks(range(11),[r['low'] for r in rows])
            ax.tick_params(length=0,labelsize=10.5,colors=c['text'],pad=7)
            ax.grid(axis='x',color=c['grid'],linewidth=.5);ax.set_axisbelow(True)
        left,right=axes
        for y,r in enumerate(rows):
            left.plot([r['long_stock_gain'],r['short_stock_gain']],[y,y],c=c['grid'],lw=2)
            left.plot(r['long_stock_gain'],y,'o',c=c['long'],ms=6,label='Long stocks' if y==0 else None)
            left.plot(r['short_stock_gain'],y,'s',c=c['short'],ms=6,label='Shorted stocks' if y==0 else None)
            right.barh(y,r['net_pnl'],height=.5,color=c['long'] if r['net_pnl']>=0 else c['short'])
            value=r['net_pnl'];label=f'{value:+.2f}'.replace('-','−')
            right.text(value+(.3 if value>=0 else -.3),y,label,va='center',ha='left' if value>=0 else 'right',fontsize=10.5,color=c['text'])
        left.set_xlim(-10,110);left.set_xticks([0,25,50,75,100]);left.axvline(0,c=c['text'],lw=.5)
        right.set_xlim(-12,20);right.set_xticks([-10,0,10,20]);right.axvline(0,c=c['text'],lw=.6)
        left.set_title('Stock gains per unit exposure (%)',loc='left',fontsize=11.5,fontweight='bold',color=c['text'],pad=35)
        right.set_title('Actual net P&L (points)',loc='left',fontsize=11.5,fontweight='bold',color=c['text'],pad=14)
        left.legend(loc='lower left',bbox_to_anchor=(0,1),ncol=2,frameon=False,fontsize=10,
                    labelcolor=c['text'],handletextpad=.3,columnspacing=.8,borderaxespad=0)
        if not mobile:right.set_yticklabels([])
        fig.subplots_adjust(left=.27 if mobile else .13,right=.98,bottom=.055 if mobile else .10,
                            top=.91 if mobile else .84,hspace=.35,wspace=.16)
        suffix=('' if horizon==63 else f'-{horizon}')+('_mobile' if mobile else '')+('_dark' if dark else '')
        target=OUTPUT/f'recoveries{suffix}.svg'
        fig.savefig(target,metadata={'Date':None})
        target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
        plt.close(fig)

if __name__=='__main__':
    data=json.loads((OUTPUT/'recoveries.json').read_text())
    for horizon in [21,63,126]:
        rows=[r for r in data['episodes'] if r['horizon']==horizon]
        assert len(rows)==11 and all(r['complete'] for r in rows)
        assert all(-10<=r[k]<=110 for r in rows for k in ['long_stock_gain','short_stock_gain'])
        assert all(-12<=r['net_pnl']<=17 for r in rows)
        for dark in [False,True]:
            for mobile in [False,True]:render(rows,dark,mobile,horizon)
