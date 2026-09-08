"""Render strategy-level exhibits from verified, local-only ledger aggregates."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def axis_style(ax, colors):
    ax.set_facecolor(colors["background"])
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0, colors=colors["text"], labelsize=11)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=colors["grid"], linewidth=.5)


def history(data, colors, mobile):
    rows=data["history"]
    dates=[dt.date.fromisoformat(r["date"]) for r in rows]
    fig,axes=plt.subplots(3,1,sharex=True,figsize=(5 if mobile else 8.8,7.0),
                          gridspec_kw={"height_ratios":[1.6,1,1]})
    for ax in axes:
        axis_style(ax,colors)
        ax.set_xlim(dates[0],dates[-1])
        ax.axvspan(dt.date(2022,12,29),dt.date(2023,2,2),color=colors["negative"],alpha=.18)
    axes[0].plot(dates,[r["cumulative_pp"] for r in rows],color=colors["accent"],lw=1.4)
    axes[1].fill_between(dates,[r["drawdown_pp"] for r in rows],0,color=colors["negative"],alpha=.65)
    annual=data["annual"]
    periods=[(dt.date.fromisoformat(r["start"]),dt.date.fromisoformat(r["end"])) for r in annual]
    axes[2].bar([a+(b-a)/2 for a,b in periods],
                [r["net_pp"] for r in annual],width=[max(1,(b-a).days*.72) for a,b in periods],
                color=[colors["positive"] if r["net_pp"]>=0 else colors["negative"] for r in annual])
    for ax,label in zip(axes,["Cumulative net P&L (pp)","Drawdown from earlier peak (pp)","Calendar-period net P&L (pp)"]):
        ax.text(0,1.06,label,transform=ax.transAxes,color=colors["text"],fontsize=11,weight="bold")
    axes[2].xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 4))
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.subplots_adjust(left=.14 if mobile else .09,right=.99,top=.95,bottom=.07,hspace=.40)
    return fig


def exposures(data,colors,mobile):
    fig,axes=plt.subplots(2,1,sharex=True,figsize=(5 if mobile else 8.8,5.8))
    pairs=[[("size","Size",colors["accent"],"-"),("momentum","Momentum",colors["positive"],"--")],
           [("volatility","Volatility",colors["negative"],"-"),("beta","Beta",colors["accent"],"--")]]
    for ax,series in zip(axes,pairs):
        axis_style(ax,colors)
        ax.axhline(0,color=colors["text"],lw=.6)
        for factor,label,color,style in series:
            rows=[r for r in data["factor_monthly"] if r["factor"]==factor]
            ax.plot([dt.date.fromisoformat(r["date"]) for r in rows],[r["exposure"] for r in rows],
                    label=label,color=color,ls=style,lw=1.7)
        ax.legend(loc="upper center",bbox_to_anchor=(.5,1.25),ncol=2,frameon=False,
                  labelcolor=colors["text"],fontsize=11)
        ax.axvspan(dt.date(2022,12,29),dt.date(2023,2,2),color=colors["negative"],alpha=.13)
    axes[0].set_ylabel("Signed exposure",color=colors["text"],fontsize=11)
    axes[1].set_ylabel("Signed exposure",color=colors["text"],fontsize=11)
    axes[1].xaxis.set_major_locator(mdates.YearLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].set_xlim(dt.date(2021,1,1),dt.date(2026,5,27))
    fig.subplots_adjust(left=.16 if mobile else .10,right=.98,top=.89,bottom=.08,hspace=.48)
    return fig


def factor_comparison(data,colors,mobile):
    labels={"beta":"Beta","volatility":"Volatility","momentum":"Momentum","size":"Size",
            "reversal":"Reversal","market":"Intercept","idio_pnl":"Residual",
            "unmodeled_pnl":"Uncovered holdings","price_basis_gap":"Reconciliation",
            "costs":"Trading costs","sectors":"Sector effects"}
    order=["beta","volatility","momentum","size","reversal","sectors","market",
           "idio_pnl","unmodeled_pnl","price_basis_gap","costs"]
    pnl={k:0.0 for k in order}; risk={k:0.0 for k in order}
    for row in data["factor_periods"]["episode"]:
        key="sectors" if row["factor"].startswith("sector:") else row["factor"]
        pnl[key]+=row["pnl_pp"]
    for row in data["factor_risk_episode"]:
        key="sectors" if row["factor"].startswith("sector:") else row["factor"]
        risk[key]+=row["vol_contribution_pp"]
    assert abs(sum(pnl.values())-data["periods"]["episode"]["net_pp"])<1e-8
    fig,axes=plt.subplots(2 if mobile else 1,1 if mobile else 2,
                          figsize=(5,11.6) if mobile else (8.8,5.7))
    for ax,values,title in zip(axes,[pnl,risk],["P&L contribution (pp)","Contribution to volatility (pp)"]):
        axis_style(ax,colors)
        ax.grid(False);ax.grid(axis="x",color=colors["grid"],lw=.5)
        amounts=[values[k] for k in order]
        ax.barh(range(len(order)),amounts,color=[colors["positive"] if v>=0 else colors["negative"] for v in amounts],height=.63)
        ax.set_yticks(range(len(order)),[labels[k] for k in order]);ax.invert_yaxis()
        ax.axvline(0,color=colors["text"],lw=.6)
        ax.set_title(title,color=colors["text"],fontsize=11,loc="left",pad=14)
        extent=max(amounts)-min(amounts)
        ax.set_xlim(min(0,min(amounts))-.18*extent,max(amounts)+.2*extent)
        for y,v in enumerate(amounts):
            ax.annotate(f"{v:+.2f}",(v,y),xytext=(4 if v>=0 else -4,0),textcoords="offset points",
                        ha="left" if v>=0 else "right",va="center",fontsize=10,color=colors["text"])
    if not mobile:
        axes[1].set_yticklabels([])
    fig.subplots_adjust(left=.36 if mobile else .23,right=.97,top=.94,bottom=.06,
                        hspace=.25,wspace=.13)
    return fig


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--source-sha256",required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    raw=args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.source_sha256:
        raise ValueError("Aggregate source hash differs from reviewed input")
    data=json.loads(raw)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for dark in [False,True]:
        colors={"background":"#171d24" if dark else "#ffffff","text":"#e4eaf0" if dark else "#263747",
                "grid":"#43505f" if dark else "#d6dfe5","positive":"#57bdab" if dark else "#268b7b",
                "negative":"#e69482" if dark else "#bd6559","accent":"#8bb6ee" if dark else "#3a689c"}
        with plt.rc_context({"font.family":"Arial","svg.fonttype":"none","svg.hashsalt":"attribution-history"}):
            for mobile in [False,True]:
                for name,renderer in [("strategy-history",history),("style-exposures",exposures),("episode-factors-risk",factor_comparison)]:
                    fig=renderer(data,colors,mobile)
                    suffix=("_mobile" if mobile else "")+("_dark" if dark else "")
                    destination=args.output_dir/f"{name}{suffix}.svg"
                    fig.savefig(destination,facecolor=colors["background"],metadata={"Date":None})
                    destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines())+"\n")
                    plt.close(fig)


if __name__=="__main__":
    main()
