/* Shared static chart renderer. Daily observations remain authoritative. */
(function (root) {
  'use strict';
  // Each series keeps its identity across articles and themes.
  const PALETTE = {
    strategy:['#27322f','#d7deda'], long:['#426e89','#89b5cc'], short:['#606e77','#a0acb4'],
    comparison:['#78848a','#8a969f'], index:['#896835','#c4a36f'], hedged:['#736582','#b6a5c8'], cash:['#427a70','#85b9aa'],
    momentum:['#426e89','#89b5cc'], reversal:['#9b626e','#d39aaa'], low_volatility:['#736582','#b6a5c8'],
    size:['#896835','#c4a36f'], liquidity:['#427a70','#85b9aa'], market:['#606e77','#a0acb4'], short_interest:['#27322f','#d7deda'],
    low_risk:['#426e89','#89b5cc'], beta:['#736582','#b6a5c8'], sector:['#78848a','#8a969f'], residual:['#606e77','#a0acb4'],
    blend:['#365e79','#8cbdd5'],
    equity_ridge:['#596877','#aab3bf'], equity_lightgbm:['#2262ab','#81b4f3'],
    equity_small_four:['#945614','#e9bc83'], equity_small_six:['#5c55a3','#b9b0fa'],
    equity_medium:['#397744','#a9ccaa'], equity_rolling:['#9c3d58','#e3a2b3']};
  const isDark=()=>typeof document!=='undefined'&&document.documentElement.dataset.theme==='dark';
  const COLORS = Object.freeze(Object.defineProperties({},Object.fromEntries(Object.entries(PALETTE).map(
    ([role,[light,dark]])=>[role,{enumerable:true,get:()=>isDark()?dark:light}]))));
  // The plot area is painted in the page colour: Plotly outlines its hover line in the plot colour,
  // and a transparent plot is treated as white, which drew a bright line in dark mode.
  const plotSurface=()=>isDark()?'#0d1117':'#ffffff';
  const signedColorScale=()=>[[0,isDark()?'#d5a081':'#976047'],[.5,isDark()?'#20282b':'#f5f4ef'],[1,isDark()?'#86bfd1':'#396a83']];
  // Plotly's default hover box is white; match it to the page in both themes.
  function hoverStyle() {
    const dark=isDark();
    return {bgcolor:dark?'#161b22':'#ffffff',bordercolor:dark?'#30363d':'#d0d7de',
      font:{family:'Bricolage Grotesque, sans-serif',size:12,color:dark?'#dce3eb':'#27343d'}};
  }

  function stats(values, annualization=252, additive=false) {
    if (values.length < 2) return null;
    const first=values[0];
    const mean=first+values.reduce((sum,value)=>sum+(value-first),0)/values.length;
    const volatility=Math.sqrt(values.reduce((a,b)=>a+(b-mean)**2,0)/(values.length-1)*annualization);
    let balance=additive?0:1, peak=balance, drawdown=0, underwater=0, longest=0;
    for (const value of values) {
      if (!Number.isFinite(value) || (!additive && value<=-1)) throw new Error('Invalid return');
      balance=additive?balance+value:balance*(1+value);
      peak=Math.max(peak,balance);
      drawdown=Math.min(drawdown,additive?balance-peak:balance/peak-1);
      // An exactly recovered peak can differ by a few rounding units after summation.
      const tolerance=8*Number.EPSILON*(additive?Math.max(1,Math.abs(peak)):peak);
      underwater=peak-balance>tolerance?underwater+1:0;
      longest=Math.max(longest,underwater);
    }
    return {annual_return:additive?mean*annualization:Math.expm1(Math.log(balance)*annualization/values.length),
      volatility, sharpe:volatility?mean*annualization/volatility:null, drawdown, underwater_sessions:longest};
  }

  function path(values, first, last, initial=100) {
    let growth=initial, peak=initial;
    const equity=[initial], drawdown=[0];
    for (let i=first+1;i<=last;i++) {
      growth*=1+values[i]; peak=Math.max(peak,growth);
      equity.push(growth); drawdown.push(growth/peak-1);
    }
    return {equity,drawdown};
  }

  function narrowGrowthTicks(low,high) {
    if(!(low>0&&high>low&&high/low<2))return null;
    const rough=(high-low)/4,order=10**Math.floor(Math.log10(rough));
    const step=order*[1,2,2.5,5,10].find(n=>n*order>=rough);
    const first=Math.floor(low/step),last=Math.ceil(high/step);
    return Array.from({length:last-first+1},(_,i)=>Number(((first+i)*step).toPrecision(8))).filter(t=>t>0);
  }

  function linked(values, parent, first, last) {
    let growth=1, contribution=0;
    const result=[0];
    for (let i=first+1;i<=last;i++) {
      contribution+=growth*values[i]; growth*=1+parent[i]; result.push(contribution*100);
    }
    return result;
  }

  function additivePath(values,first,last) {
    let sum=0,peak=0;const equity=[0],drawdown=[0];
    for(let i=first+1;i<=last;i++){sum+=values[i]*100;peak=Math.max(peak,sum);equity.push(sum);drawdown.push(sum-peak);}
    return {equity,drawdown};
  }

  // Weekly display only for long windows; preserve endpoints and daily extrema.
  // Statistics and drawdown calculations always use the complete daily observations.
  function displayIndices(dates, arrays) {
    if (dates.length <= 1300) return dates.map((_,i)=>i);
    const selected=new Set([0,dates.length-1]);
    let start=0;
    function week(d) { return Math.floor((Date.parse(d)/86400000+3)/7); }
    for (let end=1;end<=dates.length;end++) {
      if (end<dates.length && week(dates[end])===week(dates[start])) continue;
      selected.add(end-1);
      for (const values of arrays) {
        let low=start,high=start;
        for(let j=start+1;j<end;j++) {
          if(values[j]<values[low]) low=j;
          if(values[j]>values[high]) high=j;
        }
        selected.add(low); selected.add(high);
      }
      start=end;
    }
    return [...selected].sort((a,b)=>a-b);
  }

  const api={COLORS,signedColorScale,stats,path,narrowGrowthTicks,linked,additivePath,displayIndices,displayPeriods};
  if (typeof module!=='undefined') module.exports=api;
  root.BlogCharts=api;
  if (!root.document) return;
  const documents=new Map();
  const pendingCharts=new Map();
  const chartObserver='IntersectionObserver' in root ? new root.IntersectionObserver(entries=>{
    for(const entry of entries)if(entry.isIntersecting) {
      const start=pendingCharts.get(entry.target);
      pendingCharts.delete(entry.target);chartObserver.unobserve(entry.target);
      if(start)start();
    }
  },{rootMargin:'600px 0px'}) : null;
  function whenVisible(host,start) {
    host.classList.add('chart-pending');
    const run=()=>Promise.resolve().then(start).finally(()=>host.classList.remove('chart-pending'));
    if(chartObserver){pendingCharts.set(host,run);chartObserver.observe(host);}else run();
  }
  function load(url) {
    if (!documents.has(url)) documents.set(url,fetch(url).then(r=>{
      if(!r.ok) throw new Error('Chart data unavailable'); return r.json();
    }));
    return documents.get(url);
  }
  function plotly() {
    if(!root.__plotlyPromise) root.__plotlyPromise=root.Plotly ? Promise.resolve() : new Promise((resolve,reject)=>{
      const script=document.createElement('script');
      script.src='https://cdn.jsdelivr.net/npm/plotly.js-cartesian-dist-min@3.1.0/plotly-cartesian.min.js';
      script.onload=resolve; script.onerror=reject; document.head.append(script);
    });
    return root.__plotlyPromise;
  }
  function element(tag,className,text) {
    const el=document.createElement(tag); if(className) el.className=className;
    if(text!==undefined) el.textContent=text; return el;
  }
  // Explore panels share one layout: a captioned row per group of controls.
  function controlRow(parent,caption) {
    const row=element('div','blog-chart-row'),body=element('div','blog-chart-controls');
    row.append(element('span','blog-chart-row-label',caption),body);parent.append(row);return body;
  }
  function buttonGroup(label,className) {
    const group=element('div',className);
    group.setAttribute('role','group');
    group.setAttribute('aria-label',label);
    return group;
  }
  // Both episodes compare the same books, so one key controls both plots.
  function sharedSeriesKey(group,series,visible,redraw,label='Series in both episodes') {
    let key=group.querySelector('.shared-series');
    if(!key) {
      key=element('div','shared-series');
      key.setAttribute('role','group');key.setAttribute('aria-label',label);
      for(const item of series) {
        const button=element('button','',item.label);button.type='button';
        button.dataset.series=item.id;
        button.dataset.dash=item.dash||'solid';
        button.setAttribute('aria-pressed',String(visible.get(item.id)));
        const [light,dark]=PALETTE[item.role]||PALETTE.comparison;
        button.style.setProperty('--series-light',light);button.style.setProperty('--series-dark',dark);
        button.onclick=()=>{
          button.setAttribute('aria-pressed',String(button.getAttribute('aria-pressed')!=='true'));
          key.dispatchEvent(new Event('serieschange'));
        };
        key.append(button);
      }
      group.prepend(key);
    }
    const read=()=>{for(const button of key.children)visible.set(button.dataset.series,button.getAttribute('aria-pressed')==='true');};
    read();
    key.addEventListener('serieschange',()=>{read();redraw();});
  }
  function dateRange(parent,start,end) {
    const wrap=element('div','blog-chart-range');
    start.setAttribute('aria-label','Start date');end.setAttribute('aria-label','End date');
    wrap.append(start,element('span','blog-chart-range-sep','–'),end);parent.append(wrap);
  }
  function checkControl(parent,label,checked,change) {
    const wrap=element('label','blog-chart-check'),box=element('input');box.type='checkbox';box.checked=checked;
    box.onchange=()=>change(box.checked);wrap.append(box,element('span','',label));parent.append(wrap);return {wrap,box};
  }
  function displayPeriods(episodes,dates,rebased) {
    return (episodes||[]).map(([label,opening,end])=>{
      // When a period starts on a holiday, rebase to the preceding close.
      const start=rebased&&!dates.includes(opening)?dates.findLast(d=>d<opening)||opening:opening;
      if(!/^(Development|Later( period)?|After \d{4}|Post-\d{4}|Test:.*)$/i.test(label))return [label,start,end];
      const first=dates.find(date=>(rebased?date>start:date>=start)&&date<=end);
      if(!first)return [label,start,end];
      const last=new Date(end+'T00:00:00Z');
      const endLabel=last.getUTCMonth()===11?end.slice(0,4):
        last.toLocaleDateString('en',{month:'short',year:'numeric',timeZone:'UTC'});
      return [first.slice(0,4)===endLabel?endLabel:first.slice(0,4)+'–'+endLabel,start,end];
    });
  }
  function rangePresets(extra,full,episodes,current,apply,{fullLabel='Full history',compare=false}={}) {
    const presets=[],clamp=([a,b])=>[a<full[0]?full[0]:a,b>full[1]?full[1]:b];let chosen=null;
    function add(group,label,target,mode='window') {
      const button=element('button','',label),preset={button,target,mode};button.type='button';
      button.onclick=()=>{chosen=preset;apply(...target(),mode);};group.append(button);presets.push(preset);
    }
    const periods=buttonGroup('Chart period','blog-chart-periods');
    extra.before(periods);
    add(periods,fullLabel,()=>full,'full');
    if(compare)add(periods,'Both drawdowns',()=>full,'compare');
    for(const [label,a,b] of episodes) {
      if(b<full[0]||a>full[1]||(a<=full[0]&&b>=full[1]))continue;
      add(periods,label,()=>clamp([a,b]));
    }
    const named=periods.children.length>1;
    const windows=named?buttonGroup('Window length','blog-chart-segments'):periods;
    if(named)controlRow(extra,'Window').append(windows);
    const lengths=(Date.parse(full[1])-Date.parse(full[0]))/86400000>365*3?[12,36,60]:[3,6,12];
    function trailing(end,months) {
      const d=new Date(end+'T00:00:00Z'),day=d.getUTCDate();
      d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()-months+1,0);
      d.setUTCDate(Math.min(day,d.getUTCDate()));return d.toISOString().slice(0,10);
    }
    for(const months of lengths) {
      if(trailing(full[1],months)<=full[0])continue;
      add(windows,months%12?months+'M':months/12+'Y',()=>{
        const end=named?current()[1]:full[1];return clamp([trailing(end,months),end]);
      });
    }
    return (range,mode='window')=>{
      const shows=preset=>{const [a,b]=preset.target();return a===range[0]&&b===range[1]&&((preset.mode==='compare')===(mode==='compare'));};
      const pressed=chosen&&shows(chosen)?chosen:presets.find(shows);
      for(const preset of presets)preset.button.setAttribute('aria-pressed',String(preset===pressed));
    };
  }
  function format(value,percent=false) {
    return value===null || !Number.isFinite(value) ? '—' :
      (percent ? (value*100).toFixed(1)+'%' : value.toFixed(2));
  }
  function periodChoices(ui,labels,change,label='Chart period') {
    const group=buttonGroup(label,'blog-chart-periods');
    const select=index=>Array.from(group.children).forEach((button,i)=>{
      button.setAttribute('aria-pressed',String(i===index));
    });
    ui.prepend(group);
    labels.forEach((label,index)=>{
      const button=element('button','',label);button.type='button';
      button.onclick=()=>{select(index);change(index);};
      group.append(button);
    });
    select(0);
    return select;
  }
  function refitPeriod(ui,years,split,redraw) {
    if(!Number.isFinite(split))return ()=>true;
    const first=Math.min(...years),last=Math.max(...years);
    let selected=[first,last];
    if(split>first&&split<=last) {
      const ranges=[selected,[first,split-1],[split,last]];
      periodChoices(ui,['Full history',first+'–'+(split-1),split+'–'+last],index=>{
        selected=ranges[index];redraw();
      });
    }
    return year=>year>=selected[0]&&year<=selected[1];
  }

  // Fixed matrices share typography, theme handling and loading with time series.
  async function matrix(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const inPeriod=refitPeriod(ui,cfg.columns.map(Number),Number(host.dataset.refitSplit),draw);
    const defaults=cfg.rows.map((_,i)=>i).slice(0,cfg.defaultCount||cfg.rows.length);
    let selected=new Set(defaults);
    const boxes=[],rowLabels=[];
    if(cfg.defaultCount) {
      const extra=element('details','blog-chart-options');extra.append(element('summary','','Explore'));ui.append(extra);
      const controls=controlRow(extra,'Select');
      const reset=element('button','','Top '+cfg.defaultCount),clear=element('button','','Clear');
      reset.type=clear.type='button';controls.append(reset,clear);
      const search=element('input');search.type='search';search.placeholder='Find a predictor or theme';search.setAttribute('aria-label','Find a predictor or theme');controls.append(search);
      const choices=element('div','blog-chart-predictors');choices.setAttribute('role','group');choices.setAttribute('aria-label','Predictors to show');extra.append(choices);
      cfg.rows.forEach((name,i)=>{
        const {wrap:label,box}=checkControl(choices,cfg.descriptions[i],selected.has(i),checked=>{if(checked)selected.add(i);else selected.delete(i);draw();});
        boxes.push(box);rowLabels.push(label);
      });
      search.oninput=()=>rowLabels.forEach((label,i)=>label.hidden=!((cfg.rows[i]+' '+cfg.descriptions[i]).toLowerCase().includes(search.value.trim().toLowerCase())));
      reset.onclick=()=>{selected=new Set(defaults);search.value='';rowLabels.forEach(label=>label.hidden=false);draw();};
      clear.onclick=()=>{selected.clear();draw();};
      extra.append(element('p','blog-chart-note','Top '+cfg.defaultCount+' uses mean absolute coefficient across all refits. Colours retain the sign and the same scale across selections.'));
    }
    const graph=element('div','blog-chart-plot');ui.append(graph);
    const selectionLabel=element('p','blog-chart-window');selectionLabel.setAttribute('aria-live','polite');if(cfg.defaultCount)ui.append(selectionLabel);
    async function draw() {
      const dark=document.documentElement.dataset.theme==='dark',mobile=host.clientWidth<550;
      boxes.forEach((box,i)=>box.checked=selected.has(i));
      const indices=cfg.rows.flatMap((_,i)=>selected.has(i)?[i]:[]);
      selectionLabel.textContent=indices.length?'Showing '+indices.length+' of '+cfg.rows.length+' predictors':'Choose predictors under Explore.';
      graph.hidden=!indices.length;if(!indices.length)return;
      const height=Math.max(170,indices.length*(mobile?29:25)+100);graph.style.height=height+'px';
      function rowLabel(text) {
        const width=mobile?22:32,lines=[''];
        for(const word of text.split(' ')) {
          if(lines.at(-1).length+word.length>width&&lines.at(-1))lines.push('');
          lines[lines.length-1]+=(lines.at(-1)?' ':'')+word;
        }
        return lines.slice(0,2).join('<br>')+(lines.length>2?'…':'');
      }
      const limit=Math.max(...cfg.values.flat().map(Math.abs));
      const cols=cfg.columns.flatMap((year,j)=>inPeriod(year)?[j]:[]);
      const years=cols.map(j=>cfg.columns[j]);
      await Plotly.react(graph,[{type:'heatmap',x:years,y:indices.map(String),z:indices.map(i=>cols.map(j=>cfg.values[i][j])),
        zmin:-limit,zmax:limit,colorscale:signedColorScale(),
        xgap:1,ygap:1,customdata:indices.map(i=>cols.map(()=>cfg.descriptions[i])),
        hovertemplate:'%{customdata}<br>%{x}: %{z:.3f}<extra></extra>',
        colorbar:{orientation:'h',thickness:8,len:mobile?.85:.5,x:.5,xanchor:'center',y:-Math.max(.12,40/(height-90)),yanchor:'top',
          tickvals:[-limit,0,limit],tickformat:'.2f',tickangle:0,outlinewidth:0,title:{text:cfg.unit,side:'top',font:{size:12}}}}],
        {height,margin:{l:10,r:10,t:10,b:80},font:{family:'Bricolage Grotesque, sans-serif',size:12,color:dark?'#dce3eb':'#27343d'},
          paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),
          xaxis:{type:'category',tickangle:0,tickvals:mobile&&years.length>3?[years[0],years[Math.floor(years.length/2)],years.at(-1)]:years},
          yaxis:{type:'category',autorange:'reversed',automargin:true,tickvals:indices.map(String),ticktext:indices.map(i=>rowLabel(cfg.rows[i]))}}, {responsive:true,displayModeBar:false});
    }
    await draw();host.querySelector('.blog-chart-status').hidden=true;
    new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;
    new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }

  async function mount(host) {
    const status=host.querySelector('.blog-chart-status');
    try {
      const data=await load(host.dataset.source);
      if(data.version!==1) throw new Error('Unsupported chart version');
      const cfg=data.charts[host.dataset.chart], bars=['bars','grouped-bars'].includes(cfg.kind);
      if(cfg.kind==='rank-bars'){rankBars(host,cfg);return;}
      await plotly();
      if(cfg.kind==='decile-profiles'){await decileProfiles(host,cfg);return;}
      if(cfg.kind==='matrix'){await matrix(host,cfg);return;}
      if(cfg.kind==='panels'){await panels(host,cfg);return;}
      if(cfg.kind==='calendar-distribution'){await calendarDistribution(host,cfg);return;}
      if(cfg.kind.startsWith('attribution')){await attribution(host,data,cfg);return;}
      const sharedGroup=host.closest('[data-shared-series]');
      const all=new Map(data.series.map(s=>[s.id,{...s,returns:s.values.map(v=>v/data.scale)}]));
      const series=cfg.series.map(id=>all.get(id));
      if(sharedGroup){
        for(const s of series)if(!s.dash)s.dash={short:'dash',index:'dot'}[s.role]||'solid';
      }
      const full=[cfg.start||data.dates[0],cfg.end||data.dates.at(-1)];
      let range=[...full], ready=false, busy=false, pending=false;
      const visible=new Map(series.map(s=>[s.id,s.visible!==false && (s.role!=='index'||cfg.benchmark===true)]));
      if(sharedGroup)sharedSeriesKey(sharedGroup,series,visible,draw);
      const optionalBoxes=new Map();
      let legendTimer;
      const ui=host.querySelector('.blog-chart-ui'); ui.hidden=false;
      if(cfg.heading)ui.append(element('p','blog-chart-heading',cfg.heading));
      const initialWealth=Number(host.dataset.initialWealth)||100;
      const extra=element('details','blog-chart-options');
      extra.append(element('summary','','Explore'));ui.append(extra);
      if(cfg.exploreOpen)extra.open=true;
      const start=element('input'),end=element('input'); start.type=end.type='date';
      [start,end].forEach(input=>{input.min=full[0];input.max=full[1];});
      function setRange(a,b) {
        if(a>b || b<full[0] || a>full[1]) {start.value=range[0];end.value=range[1];return;}
        range=[a<full[0]?full[0]:a,b>full[1]?full[1]:b]; draw();
      }
      const episodes=displayPeriods(cfg.episodes,data.dates,cfg.kind==='performance');
      const markPresets=rangePresets(extra,full,episodes,()=>range,setRange,{fullLabel:sharedGroup?'Full episode':'Full history'});
      dateRange(controlRow(extra,'Dates'),start,end);
      start.onchange=end.onchange=()=>{if(start.value&&end.value)setRange(start.value,end.value);};
      const barMetrics=[
        ['annual_return','Annual return (%)','.0%','.1%'],
        ['sharpe','Sharpe ratio','.2f','.2f'],
        ['volatility','Volatility (%)','.0%','.1%']
      ];
      let barMetric=barMetrics[0];
      if(cfg.kind==='grouped-bars') {
        const select=element('select');select.setAttribute('aria-label','Metric');
        for(const [key,title] of barMetrics) {
          const option=element('option','',title);option.value=key;select.append(option);
        }
        select.onchange=()=>{barMetric=barMetrics.find(([key])=>key===select.value);draw();};
        controlRow(extra,'Metric').append(select);
      }
      let benchmarkBox;
      const benchmark=series.find(s=>s.role==='index');
      let show=null;
      function checkbox(label,checked,change) {
        show??=controlRow(extra,'Show');return checkControl(show,label,checked,change).box;
      }
      if(benchmark&&!sharedGroup) benchmarkBox=checkbox(bars?benchmark.label:'Market',visible.get(benchmark.id),value=>{visible.set(benchmark.id,value);draw();});
      for(const s of series.filter(s=>s!==benchmark&&(s.visible===false||cfg.showLegend===false||initialWealth===1)))optionalBoxes.set(s.id,
        checkbox(s.label,visible.get(s.id),value=>{visible.set(s.id,value);draw();}));
      const volatilityTarget=cfg.additive&&cfg.volatilityTarget;
      const volatilityLabel=volatilityTarget?format(volatilityTarget,true).replace('.0%','%'):'';
      let scaleBox,scaleStatus;
      if(volatilityTarget) {
        const control=element('div','blog-chart-volatility');
        ui.append(control);
        scaleBox=checkControl(control,'Rescale to '+volatilityLabel+' annualized volatility',cfg.matchVolatilityByDefault===true,draw).box;
        scaleStatus=element('p','blog-chart-note','Choose a longer window with variation in every portfolio to match volatility.');
        scaleStatus.setAttribute('role','status');scaleStatus.hidden=true;ui.append(scaleStatus);
      }
      const graph=element('div','blog-chart-plot');ui.append(graph);
      const windowLabel=element('p','blog-chart-window');windowLabel.setAttribute('aria-live','polite');ui.append(windowLabel);
      if(cfg.controlsBelow)windowLabel.after(extra);
      const statisticsPanel=element('details','blog-chart-statistics');statisticsPanel.open=cfg.statisticsOpen??false;
      statisticsPanel.append(element('summary','','Window statistics'));ui.append(statisticsPanel);
      const tableWrap=element('div','blog-chart-table-wrap'); statisticsPanel.append(tableWrap);
      const table=element('table');tableWrap.append(table);
      table.setAttribute('aria-label','Selected-window statistics');
      const head=element('thead'),hr=element('tr');head.append(hr);table.append(head);
      const headings=['Series',cfg.additive?'Annual P&L / return':'Annual growth','Ann. volatility','Sharpe','Max drawdown'];
      if(cfg.drawdown)headings.push('Longest drawdown (sessions)');
      headings.forEach(label=>{const th=element('th','',label);th.scope='col';hr.append(th);});
      const body=element('tbody');table.append(body);
      if(cfg.note)statisticsPanel.append(element('p','blog-chart-note',cfg.note));
      if(cfg.drawdown)statisticsPanel.append(element('p','blog-chart-note','Longest drawdown counts consecutive trading sessions below the previous peak, including a decline still open at the end of the window.'));
      if(cfg.kind==='values'||cfg.statistics===false)statisticsPanel.hidden=true;
      function updateTable(plottedSeries,first,last) {
        body.replaceChildren();
        for(const s of plottedSeries.filter(s=>visible.get(s.id)&&!s.contribution)) {
          const m=stats(s.returns.slice(first+(bars?0:1),last+1),data.annualization,s.additive);
          const row=element('tr'),label=element('th','',bars&&s.id.startsWith('decile_')?'Decile '+s.label:s.label);label.scope='row';row.append(label);
          for(const key of ['annual_return','volatility','sharpe','drawdown'])row.append(element('td','',m?(s.additive&&key==='drawdown'?(m[key]*100).toFixed(1)+' pp':format(m[key],key!=='sharpe')):'—'));
          if(cfg.drawdown)row.append(element('td','',m?String(m.underwater_sessions):'—'));
          body.append(row);
        }
        if(!body.children.length) {const row=element('tr'),td=element('td','','Choose a series to see its statistics.');td.colSpan=headings.length;row.append(td);body.append(row);}
      }
      function theme() {
        const dark=document.documentElement.dataset.theme==='dark';
        return {text:dark?'#dce3eb':'#27343d',grid:dark?'#36404a':'#e2e7eb',paper:dark?'#15191e':'#ffffff'};
      }
      async function draw() {
        if(busy){pending=true;return;} busy=true;
        try {
          start.value=range[0];end.value=range[1];markPresets(range);
          const first=data.dates.findIndex(d=>d>=range[0]);
          let last=data.dates.length-1;while(last>=0&&data.dates[last]>range[1])last--;
          if(scaleStatus)scaleStatus.hidden=true;
          if(first<0||last<=first) {
            windowLabel.hidden=false;
            windowLabel.textContent='Choose a window containing at least two observations.';
            body.replaceChildren();graph.hidden=true;return;
          }
          graph.hidden=false;
          const dates=data.dates.slice(first,last+1),t=theme(),traces=[];
          const volatilities=scaleBox?.checked
            ? series.map(s=>stats(s.returns.slice(first+1,last+1),data.annualization)?.volatility)
            : [];
          const scaled=volatilities.length>0&&volatilities.every(value=>value>0&&Number.isFinite(value));
          if(scaleBox?.checked)scaleStatus.hidden=scaled;
          const plottedSeries=scaled?series.map((s,index)=>{
            if(!s.additive)return s;
            const multiplier=volatilityTarget/volatilities[index];
            return {...s,returns:s.returns.map(value=>value*multiplier)};
          }):series;
          const mobile=host.clientWidth<550;
          const labelEnds=cfg.directLabels || (initialWealth===1 && host.clientWidth>=620);
          const showLegend=!sharedGroup && cfg.showLegend!==false && !(initialWealth===1 && labelEnds);
          let plotHeight=cfg.drawdown||cfg.contributions?405:300;
          if(bars)plotHeight=430;
          if(initialWealth===1)plotHeight=mobile?425:470;
          if(sharedGroup)plotHeight=sharedGroup.clientWidth<550?300:335;
          const layout={autosize:true,height:plotHeight,
            margin:{l:mobile?44:50,r:12,t:bars?26:!showLegend?28:mobile?69:57,b:33},font:{family:'Bricolage Grotesque, sans-serif',size:mobile?11.5:12,color:t.text},
            paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),hovermode:bars?'closest':'x unified',
            modebar:{color:t.text,bgcolor:'rgba(0,0,0,0)',activecolor:COLORS.strategy},
            dragmode:'zoom',showlegend:showLegend,legend:{orientation:'h',y:1.10,yanchor:'bottom',x:0,font:{size:mobile?11:12},groupclick:'togglegroup'},
            xaxis:{type:bars?'category':'date',gridcolor:t.grid,showgrid:false,automargin:true,
              spikecolor:isDark()?'#8b949e':'#6e7681',spikethickness:1,spikedash:'solid'},
            yaxis:{gridcolor:t.grid,zerolinecolor:t.grid,automargin:true},annotations:[]};
          const color=s=>COLORS[s.role]||COLORS.comparison;
          function trace(s,x,y,extra={}) {
            const width=cfg.emphasis ? (s.id===cfg.emphasis?2.8:1.2) : s.role==='index'?1.3:1.8;
            return {type:'scatter',mode:'lines',x,y,name:s.label,legendgroup:s.id,
              visible:visible.get(s.id)?true:'legendonly',showlegend:(s.role!=='index'&&s.visible!==false)||visible.get(s.id),
              line:{color:color(s),width,dash:s.dash||'solid'},
              hovertemplate:'%{x|%d %b %Y}<br>%{y:.2f}<extra>%{fullData.name}</extra>',...extra};
          }
          function heading(text,y,yshift=0) {layout.annotations.push({text,x:0,y,yshift,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false,font:{size:13,color:t.text}});}
          if(cfg.kind==='grouped-bars') {
            const [metric,title,tickformat,hoverformat]=barMetric;
            layout.height=280;layout.margin.t=62;layout.barmode='group';layout.bargap=.3;
            layout.yaxis.tickformat=tickformat;layout.xaxis.title={text:'Decile (1 = lowest score)',font:{size:12}};
            heading(title,1);
            const groups=[...new Set(series.map(s=>s.group))];
            for(const group of groups) {
              const items=series.filter(s=>s.group===group);
              traces.push({type:'bar',name:group,legendgroup:items[0].id,
                x:items.map(s=>s.category),y:items.map(s=>stats(s.returns.slice(first,last+1),data.annualization)?.[metric]),
                visible:visible.get(items[0].id)?true:'legendonly',marker:{color:color(items[0])},
                hovertemplate:group+' · decile %{x}<br>'+title+': %{y:'+hoverformat+'}<extra></extra>'});
            }
          } else if(bars) {
            const shown=series.filter(s=>visible.get(s.id));
            const specs=[['sharpe','Sharpe ratio','', [0.72,1]],['annual_return','Annual return (%)','.1%',[0.36,.64]],['volatility','Volatility (%)','.1%',[0,.28]]];
            for(const [panel,[key,title,format,domain]] of specs.entries()) {
              const suffix=panel?String(panel+1):'';
              layout['xaxis'+suffix]={type:'category',anchor:'y'+suffix,showgrid:false,tickmode:'array',tickvals:shown.map(s=>s.label),ticktext:shown.map(s=>s.tick||s.label),categoryorder:'array',categoryarray:shown.map(s=>s.label)};
              layout['yaxis'+suffix]={domain,anchor:'x'+suffix,gridcolor:t.grid,zerolinecolor:t.grid,tickformat:format,rangemode:'tozero'};
              heading(title,domain[1]);
              traces.push({type:'bar',x:shown.map(s=>s.label),
                y:shown.map(s=>stats(s.returns.slice(first,last+1),data.annualization)?.[key]),
                name:title,showlegend:false,marker:{color:shown.map(color)},
                xaxis:'x'+suffix,yaxis:'y'+suffix,
                hovertemplate:'%{x}<br>'+title+': %{y'+(format?':'+format:':.2f')+'}<extra></extra>'});
            }
            layout.barmode='overlay';layout.legend.y=1.10;
          } else {
            layout.xaxis.range=range;layout.xaxis.autorange=false;
            layout.xaxis.ticklabelstandoff=cfg.dateLabelSpacing??0;
            const secondary=cfg.drawdown||cfg.contributions;
            layout.xaxis.anchor=secondary?'y2':'y';
            layout.yaxis.domain=secondary?[.43,1]:[0,1];layout.yaxis.type=cfg.log?'log':'linear';
            if(cfg.growthRange&&range[0]===full[0]&&range[1]===full[1])layout.yaxis.range=cfg.growthRange;
            if(cfg.log) {
              const ticks=[];
              if(initialWealth===1)for(let exponent=-10;exponent<20;exponent++)ticks.push(2**exponent);
              else for(let exponent=-3;exponent<8;exponent++)for(const n of [1,2,5])ticks.push(n*10**exponent);
              layout.yaxis.tickmode='array';layout.yaxis.tickvals=ticks;layout.yaxis.ticktext=ticks.map(String);
            }
            const growthLabel=initialWealth===1?'Growth of $1 after fees':'Growth · 100 at selected start';
            heading(cfg.unit||(cfg.additive?(benchmark&&visible.get(benchmark.id)?'P&L (points) / market change (%)':'P&L since selected start (points)'):growthLabel+(cfg.log?' (log scale)':'')),1);
            if(cfg.dateTicks&&range[0]===full[0]&&range[1]===full[1]) {
              const ticks=mobile?(cfg.mobileDateTicks||cfg.dateTicks):cfg.dateTicks;
              layout.xaxis.tickmode='array';layout.xaxis.tickvals=ticks;layout.xaxis.ticktext=ticks.map(d=>d.slice(0,4));
            }
            if(secondary) {
              layout.yaxis2={domain:[0,.29],anchor:'x',gridcolor:t.grid,zerolinecolor:t.grid,
                tickformat:cfg.additive?'.0f':cfg.drawdown?'.0%':'.0f',ticksuffix:cfg.contributions?' pp':''};
              if(cfg.contributionRange&&range[0]===full[0]&&range[1]===full[1])layout.yaxis2.range=cfg.contributionRange;
              heading(cfg.drawdown?(cfg.drawdownUnit||(cfg.additive?'Drawdown (points)':'Drawdown (%)')):'Linked book contributions (pp)',.29,8);
            }
            for(const s of plottedSeries) {
              if(s.contribution) {
                const values=linked(s.returns,all.get(s.parent).returns,first,last);
                const indices=displayIndices(dates,[values]);
                traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values[i]),{yaxis:'y2',hovertemplate:'%{x|%d %b %Y}<br>%{y:.2f} pp<extra>%{fullData.name}</extra>'}));
              } else if(cfg.kind==='values') {
                traces.push(trace(s,dates,s.returns.slice(first,last+1)));
              } else {
                const values=s.additive?additivePath(s.returns,first,last):path(s.returns,first,last,initialWealth);
                if(cfg.additive&&!s.additive)values.equity=values.equity.map(v=>v-100);
                const indices=displayIndices(dates,[values.equity,values.drawdown]);
                traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values.equity[i]),cfg.additive?{hovertemplate:'%{x|%d %b %Y}<br>%{y:.2f}'+(s.additive?' points':'%')+'<extra>%{fullData.name}</extra>'}:{}));
                if(cfg.drawdown&&s.drawdown!==false)traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values.drawdown[i]),{yaxis:'y2',showlegend:false,hovertemplate:'%{x|%d %b %Y}<br>%{y'+(s.additive?':.2f} points':':.2%}')+'<extra>%{fullData.name}</extra>'}));
              }
            }
            if(cfg.log) {
              const extents=traces.filter(tr=>tr.yaxis!=='y2'&&tr.visible===true&&tr.y.length)
                .map(tr=>[Math.min(...tr.y),Math.max(...tr.y)]);
              const ticks=narrowGrowthTicks(Math.min(...extents.map(e=>e[0])),Math.max(...extents.map(e=>e[1])));
              if(ticks){layout.yaxis.tickvals=ticks;layout.yaxis.ticktext=ticks.map(String);}
            }
            // Optional direct labels: each visible line named at its last point, nudged apart when close.
            if(labelEnds&&traces.some(tr=>tr.yaxis!=='y2'&&tr.visible===true)) {
              const ends=traces.filter(tr=>tr.yaxis!=='y2'&&tr.visible===true&&tr.y.length)
                .map(tr=>({x:tr.x.at(-1),y:tr.y.at(-1),name:tr.name,color:tr.line.color}));
              // Leave room for the longest label so it isn't cut off at the right edge.
              layout.margin.r=Math.max(mobile?92:128,...ends.map(e=>e.name.length*(mobile?6.6:7.4)+14));
              const values=traces.filter(tr=>tr.yaxis!=='y2'&&tr.visible===true).flatMap(tr=>tr.y);
              const coordinate=y=>cfg.log?Math.log10(y):y;
              const lo=coordinate(Math.min(...values)),hi=coordinate(Math.max(...values)),plotHeight=layout.height-layout.margin.t-layout.margin.b;
              const perUnit=plotHeight*(secondary?.57:1)/((hi-lo)*1.1||1),gap=15;
              ends.sort((a,b)=>a.y-b.y);
              let previous=-Infinity;
              for(const e of ends){e.px=coordinate(e.y)*perUnit;if(e.px-previous<gap)e.px=previous+gap;previous=e.px;}
              for(const e of ends)layout.annotations.push({x:e.x,y:coordinate(e.y),text:e.name,xref:'x',yref:'y',xanchor:'left',yanchor:'middle',
                xshift:6,yshift:e.px-coordinate(e.y)*perUnit,showarrow:false,font:{size:mobile?11:12,color:e.color}});
            }
            if(cfg.marker&&range[0]<=cfg.marker&&range[1]>=cfg.marker)layout.shapes=[{type:'line',xref:'x',yref:'paper',x0:cfg.marker,x1:cfg.marker,y0:0,y1:1,line:{color:t.text,width:1,dash:'dot'}}];
            if(cfg.band)layout.shapes=[{type:'rect',xref:'paper',yref:'y',x0:0,x1:1,y0:cfg.band[0],y1:cfg.band[1],fillcolor:t.grid,opacity:.4,line:{width:0},layer:'below'}];
            if(cfg.shade)layout.shapes=[...(layout.shapes||[]),...cfg.shade.map(([a,b])=>({type:'rect',xref:'x',yref:'paper',x0:a,x1:b,y0:0,y1:1,fillcolor:t.grid,opacity:.3,line:{width:0},layer:'below'}))];
            for(const label of cfg.periodLabels||[]) {
              if(label.date<range[0]||label.date>range[1])continue;
              layout.annotations.push({x:label.date,y:label.y??.03,xref:'x',yref:'paper',
                text:mobile?(label.mobileText||label.text):label.text,showarrow:false,xanchor:'center',yanchor:'bottom',
                font:{size:mobile?10:11,color:t.text},bgcolor:t.paper,borderpad:2});
            }
            if(cfg.referenceLevel!==undefined) {
              layout.shapes=[...(layout.shapes||[]),{type:'line',xref:'paper',yref:'y',x0:0,x1:1,
                y0:cfg.referenceLevel,y1:cfg.referenceLevel,line:{color:COLORS.short,width:1},opacity:.55,layer:'below'}];
            }
            if(cfg.zeroReference) {
              layout.yaxis.zeroline=true;layout.yaxis.zerolinecolor=t.text;layout.yaxis.zerolinewidth=1;
            }
          }
          await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:mobile?false:'hover',displaylogo:false,scrollZoom:false,doubleClickDelay:300,
            modeBarButtonsToRemove:['select2d','lasso2d','autoScale2d'],toImageButtonOptions:{format:'svg',filename:'quant-notes-chart'}});
          if(!statisticsPanel.hidden)updateTable(plottedSeries,first,last);
          const fullWindow=range[0]===full[0]&&range[1]===full[1];
          const datesLabel=dates[0]+' – '+dates.at(-1);
          const scaleLabel=scaled?'Rescaled to '+volatilityLabel+' annualized volatility':'Original volatility';
          windowLabel.hidden=cfg.showWindow===false||(!cfg.showWindow&&!volatilityTarget&&fullWindow);
          windowLabel.textContent=volatilityTarget?(fullWindow?scaleLabel:datesLabel+' · '+scaleLabel):datesLabel;
          windowLabel.title=!showLegend?'Choose series under Explore.':'Click a legend entry to toggle; double-click to isolate.';
          if(benchmarkBox)benchmarkBox.checked=visible.get(benchmark.id);
          for(const [id,box] of optionalBoxes)box.checked=visible.get(id);
          if(!ready) {
            ready=true;
            graph.on('plotly_legendclick',event=>{
              clearTimeout(legendTimer);
              const id=graph.data[event.curveNumber].legendgroup;
              legendTimer=setTimeout(()=>{
                const group=all.get(id)?.group,value=!visible.get(id);
                for(const s of series)if(s.id===id||(group&&s.group===group))visible.set(s.id,value);
                draw();},320);
              return false;
            });
            graph.on('plotly_legenddoubleclick',event=>{
              clearTimeout(legendTimer);
              const id=graph.data[event.curveNumber].legendgroup;
              const group=all.get(id)?.group;
              const isolated=series.filter(s=>visible.get(s.id)).every(s=>s.id===id||(group&&s.group===group))&&visible.get(id);
              for(const s of series)visible.set(s.id,isolated?(s.visible!==false&&(s.role!=='index'||cfg.benchmark===true)):(s.id===id||(group&&s.group===group)));
              draw();return false;
            });
            graph.on('plotly_relayout',event=>{
              if(busy||bars)return;
              if(event['xaxis.autorange']){setRange(...full);return;}
              const r=event['xaxis.range']||[event['xaxis.range[0]'],event['xaxis.range[1]']];
              if(r[0]!==undefined&&r[1]!==undefined) {
                const iso=v=>new Date(v).toISOString().slice(0,10);setRange(iso(r[0]),iso(r[1]));
              }
            });
            graph.on('plotly_restyle',()=>{
              if(busy)return;
              for(const s of series) {const tr=graph.data.find(t=>t.legendgroup===s.id||(s.group&&all.get(t.legendgroup)?.group===s.group));if(tr)visible.set(s.id,tr.visible!==false&&tr.visible!=='legendonly');}
              if(benchmarkBox)benchmarkBox.checked=visible.get(benchmark.id);
              draw();
            });
            graph.on('plotly_doubleclick',()=>{if(!bars)setTimeout(()=>setRange(...full),0);});
          }
          host.querySelector('.blog-chart-fallback').hidden=true;status.hidden=true;
        } finally {busy=false;if(pending){pending=false;draw();}}
      }
      await draw();
      extra.addEventListener('toggle',()=>{if(ready)draw();});
      new MutationObserver(()=>draw()).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
      let priorWidth=host.clientWidth;
      new ResizeObserver(()=>{if(ready&&Math.abs(host.clientWidth-priorWidth)>1){priorWidth=host.clientWidth;draw();}}).observe(host);
    } catch(error) {
      host.querySelector('.blog-chart-ui').hidden=true;
      const fallback=host.querySelector('.blog-chart-fallback'),template=fallback.querySelector('template');
      if(template)fallback.append(template.content.cloneNode(true));
      status.textContent=template?'Interactive chart unavailable. The original figure is shown below.':'Interactive chart unavailable.';
      status.classList.add('blog-chart-error');
    }
  }
  async function attribution(host,data,cfg) {
    const all=new Map(data.series.map(s=>[s.id,{...s,returns:s.values.map(v=>v/data.scale)}]));
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const extra=element('details','blog-chart-options');extra.append(element('summary','','Explore'));ui.append(extra);
    const full=[data.dates[0],data.dates.at(-1)];let range=[...full],leg='total',view='full',busy=false,pending=false;
    let focus=cfg.focus||null;
    let featuredOnly=Boolean(cfg.featured);
    const expanded=new Set(focus?[focus]:[]),componentControls=new Map();
    const from=element('input'),to=element('input');from.type=to.type='date';
    for(const [input,value] of [[from,full[0]],[to,full[1]]]){input.min=full[0];input.max=full[1];input.value=value;}
    function setRange(a,b,mode='window') {
      if(a<=b&&b>=full[0]&&a<=full[1]) {
        range=[a<full[0]?full[0]:a,b>full[1]?full[1]:b];
        view=mode;
      }
      [from.value,to.value]=range;
      markPresets(range,view);draw();
    }
    from.onchange=to.onchange=()=>{if(from.value&&to.value)setRange(from.value,to.value);};
    const drawdowns=cfg.kind==='attribution-drawdowns';
    const episodes=drawdowns?cfg.windows.map(([a,b])=>[a.slice(0,4)+'–'+b.slice(2,4),a,b]):
      displayPeriods(cfg.episodes,data.dates,false);
    const markPresets=rangePresets(extra,full,episodes,()=>range,setRange,{compare:drawdowns});
    dateRange(controlRow(extra,'Dates'),from,to);
    markPresets(range,view);
    const choices=controlRow(extra,'Show');
    if(cfg.kind==='attribution') {
      const select=element('select');for(const [key,label] of [['total','Book'],['long','Long leg'],['short','Short leg']])select.add(new Option(label,key));
      select.setAttribute('aria-label','Book or leg');select.onchange=async()=>{
        const selected=select.value;select.disabled=true;
        try {
          if(selected!=='total'&&!all.has(selected+'_book')) {
            const detail=await load(cfg.legSource);
            for(const s of detail.series)all.set(s.id,{...s,returns:s.values.map(v=>v/detail.scale)});
          }
          leg=selected;await draw();
        } catch {select.value=leg;const status=host.querySelector('.blog-chart-status');status.hidden=false;status.textContent='The selected leg could not load. The current view is retained.';}
        finally {select.disabled=false;}
      };choices.append(select);
    }
    if(cfg.featured) {
      const themes=element('select');themes.setAttribute('aria-label','Themes to display');
      themes.add(new Option('Themes discussed here','featured'));themes.add(new Option('All themes','all'));
      themes.onchange=()=>{featuredOnly=themes.value==='featured';draw();};
      choices.append(themes);
    }
    if(cfg.focus) {
      const select=element('select');select.setAttribute('aria-label','Theme view');
      select.add(new Option(all.get('total_'+cfg.focus).label,cfg.focus));select.add(new Option('All themes','all'));
      select.onchange=()=>{focus=select.value==='all'?null:cfg.focus;expanded.clear();if(focus)expanded.add(focus);draw();};choices.append(select);
    }
    for(const [key,label] of [['low_risk','Low-risk components'],['activity','Trading-activity components']]) {
      componentControls.set(key,checkControl(choices,label,false,checked=>{if(checked)expanded.add(key);else expanded.delete(key);draw();}));
    }
    const graph=element('div','blog-chart-plot');ui.append(graph);
    const windowLabel=element('p','blog-chart-window');windowLabel.setAttribute('aria-live','polite');ui.append(windowLabel);
    function indices(a,b,mask,excludeStart=false){return data.dates.flatMap((d,i)=>d>=a&&d<=b&&(!excludeStart||d>a)&&(!mask||mask[i])?[i]:[]);}
    function metric(s,ids,kind) {
      if(!ids.length)return null;
      const values=ids.map(i=>s.returns[i]),sum=values.reduce((a,b)=>a+b,0),n=ids.length;
      if(kind==='total')return sum*100;
      if(kind==='return')return sum/n*252*100;
      const market=all.get('gross').returns,bs=ids.reduce((a,i)=>a+market[i],0);
      const cross=ids.reduce((a,i)=>a+s.returns[i]*market[i],0)-sum*bs/n;
      const variance=ids.reduce((a,i)=>a+market[i]**2,0)-bs**2/n;
      return variance?cross/variance*100:null;
    }
    async function draw() {
      if(busy){pending=true;return;}busy=true;
      try {
        const mobile=host.clientWidth<550,dark=document.documentElement.dataset.theme==='dark';
        const ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
        for(const [key,{wrap,box}] of componentControls){wrap.hidden=!!focus||featuredOnly;box.checked=expanded.has(key);}
        const baseKeys=focus?[focus]:featuredOnly?cfg.featured:cfg.series;
        const keys=baseKeys.filter(k=>cfg.kind==='attribution'||k!=='cost').flatMap(k=>expanded.has(k)?(cfg.kind==='attribution-years'?cfg.components[k]:[k,...cfg.components[k]]):[k]);
        if(cfg.kind==='attribution-regimes'&&!focus)keys.unshift('book');
        const nested=k=>[...expanded].some(parent=>cfg.components[parent].includes(k));
        const shown=keys.map(k=>all.get(leg+'_'+k));
        const ids=indices(...range),traces=[];
        const layout={autosize:true,margin:{l:mobile?145:160,r:20,t:45,b:45},
          font:{family:'Bricolage Grotesque, sans-serif',size:12,color:ink},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),showlegend:false,annotations:[],barmode:'overlay'};
        function title(text,x,y){layout.annotations.push({text,x,y,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false,font:{size:12}});}
        if(cfg.kind==='attribution-years') {
          const cols=mobile?(featuredOnly?1:2):Math.min(3,shown.length),rows=Math.ceil(shown.length/cols);
          layout.height=rows*(mobile?120:155)+48;layout.margin={l:37,r:8,t:32,b:24};
          const byYear=new Map();
          for(const j of ids){
            const year=Number(data.dates[j].slice(0,4));
            if(!byYear.has(year))byYear.set(year,[]);
            byYear.get(year).push(j);
          }
          const years=[...byYear.keys()];
          const annual=shown.map(series=>years.map(year=>metric(series,byYear.get(year),'return')));
          const allAnnual=annual.flat().filter(Number.isFinite);
          const low=Math.min(0,...allAnnual),high=Math.max(0,...allAnnual);
          const step=Math.max(5,Math.ceil((high-low)/20)*5);
          const bottom=Math.min(-step,Math.floor(low/step)*step),top=Math.max(step,Math.ceil(high/step)*step);
          title('Gross return (% per year)',0,1.02);
          shown.forEach((s,i)=>{
            const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix,col=i%cols,row=Math.floor(i/cols);
            const xd=[col/cols+.01,(col+1)/cols-.04],yd=[1-(row+1)/rows+.24/rows,1-row/rows-.22/rows];
            const values=annual[i];
            layout['xaxis'+suffix]={domain:xd,anchor:y,type:'linear',showgrid:false,zeroline:false,tickmode:'linear',dtick:years.length>10?10:years.length>5?5:1};
            layout['yaxis'+suffix]={domain:yd,anchor:x,range:[bottom-step*.06,top+step*.06],tickvals:[bottom,0,top],showticklabels:col===0,gridcolor:grid,zerolinecolor:COLORS.short};
            title(mobile?s.label.replace('Medium- and long-term','Med./long-term'):s.label,xd[0],yd[1]+.01);
            traces.push({type:'bar',x:years,y:values,marker:{color:values.map(v=>v<0?COLORS.short:COLORS.long)},
              xaxis:x,yaxis:y,hovertemplate:s.label+' · %{x}<br>%{y:.2f}% a year<extra></extra>'});
            const bx=[],by=[],blockDates=[];
            for(const [a,b] of [[1999,2003],[2004,2008],[2009,2013],[2014,2018],[2019,2021],[2022,2026]]) {
              const block=ids.filter(j=>Number(data.dates[j].slice(0,4))>=a&&Number(data.dates[j].slice(0,4))<=b);
              if(!block.length)continue;const value=metric(s,block,'return');
              bx.push(Number(data.dates[block[0]].slice(0,4))-.4,Number(data.dates[block.at(-1)].slice(0,4))+.4,null);by.push(value,value,null);
              const label=data.dates[block[0]]+' – '+data.dates[block.at(-1)];blockDates.push(label,label,null);
            }
            traces.push({type:'scatter',mode:'lines',x:bx,y:by,customdata:blockDates,line:{color:ink,width:1.5},xaxis:x,yaxis:y,hovertemplate:'%{customdata}<br>Block: %{y:.2f}% a year<extra></extra>'});
          });
        } else if(cfg.kind==='attribution-regimes'||cfg.kind==='attribution-drawdowns') {
          const regimes=cfg.kind==='attribution-regimes';
          const periods=regimes
            ? [['Declines',indices(...range,cfg.masks.declines)],['Strong rallies',indices(...range,cfg.masks.rallies)]]
            : (view==='compare'?cfg.windows:[range]).map(([a,b])=>[
                a.slice(0,4)+'–'+b.slice(2,4),indices(a,b,null,a!==full[0])
              ]);
          const rows=shown.map((s,i)=>({
            label:s.label,labelText:nested(keys[i])?'↳ '+s.label:cfg.components[keys[i]]?'<b>'+s.label+'</b>':s.label,
            values:periods.map(([,days])=>metric(s,days,regimes?'return':'total'))
          }));
          const unit=regimes?'Return (% of capital per year)':'P&L (points of capital)';
          const coordinates=rows.flatMap(row=>row.values).filter(Number.isFinite);
          const low=Math.min(0,...coordinates),high=Math.max(0,...coordinates),pad=(high-low||1)*.09;
          layout.height=rows.length*(mobile?31:29)+100;
          layout.margin={l:mobile?115:155,r:12,t:39,b:43};
          layout.showlegend=periods.length>1;
          layout.legend={orientation:'h',x:0,y:1.04,yanchor:'bottom',itemclick:false,itemdoubleclick:false};
          layout.xaxis={range:[low-pad,high+pad],nticks:mobile?4:6,gridcolor:grid,zerolinecolor:COLORS.short,title:{text:unit,font:{size:12}}};
          layout.yaxis={range:[rows.length-.5,-.5],tickvals:rows.map((_,i)=>i),ticktext:rows.map(row=>row.labelText.replace('Medium- and long-term return','Med./long-term return')),showgrid:false,zeroline:false,automargin:true,fixedrange:true};
          if(periods.length===2)traces.push({
            type:'scatter',mode:'lines',showlegend:false,hoverinfo:'skip',
            x:rows.flatMap(r=>[...r.values,null]),y:rows.flatMap((_,i)=>[i-.1,i+.1,null]),
            line:{color:COLORS.comparison,width:1}
          });
          periods.forEach(([name,days],j)=>{
            const first=j===0,offset=periods.length===1?0:first?-.1:.1;
            if(!days.length)layout.annotations.push({text:name+' · no observations',x:0,y:1.14+j*.09,xref:'paper',yref:'paper',showarrow:false,xanchor:'left'});
            traces.push({type:'scatter',mode:'markers',name,x:rows.map(row=>row.values[j]),y:rows.map((_,i)=>i+offset),
              marker:{size:first?8:7,symbol:first?'circle':'diamond',color:first?plotSurface():COLORS.long,line:{color:first?COLORS.short:COLORS.long,width:1.5}},
              customdata:rows.map(row=>row.label),hovertemplate:'%{customdata}<br>%{x:.2f}'+(regimes?'% per year':' points')+'<extra>'+name+'</extra>'});
          });
        } else {
          const specs=[['Return / year','return'],['Risk share','risk']];
          const stacked=host.clientWidth<295;
          layout.height=(shown.length*(mobile?25:27)+75)*(stacked?2:1);
          layout.margin={l:mobile?115:153,r:10,t:34,b:30};
          specs.forEach(([label,kind],i)=>{
            const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix;
            const values=shown.map(series=>metric(series,ids,kind));
            const xd=stacked?[0,1]:i?[.57,1]:[0,.43],yd=stacked?(i?[0,.43]:[.57,1]):[0,1];
            const lo=Math.min(0,...values),hi=Math.max(0,...values),pad=(hi-lo||1)*.12;
            layout['xaxis'+suffix]={domain:xd,anchor:y,range:[lo-pad,hi+pad],gridcolor:grid,zerolinecolor:COLORS.short,nticks:mobile?3:5,ticksuffix:'%'};
            const names=shown.map((s,j)=>{
              const name=mobile?s.label.replace('Medium- and long-term return','Med./long-term<br>return'):s.label;
              return nested(keys[j])?'↳ '+name:name;
            });
            layout['yaxis'+suffix]={domain:yd,anchor:x,type:'category',autorange:'reversed',tickvals:shown.map(s=>s.label),
              ticktext:names,showticklabels:stacked||i===0,automargin:true};
            title(label,xd[0],yd[1]+.02);
            if(!ids.length)title('No observations',xd[0],(yd[0]+yd[1])/2);
            traces.push({type:'scatter',mode:'markers',x:values,y:shown.map(s=>s.label),xaxis:x,yaxis:y,
              marker:{size:7,color:kind==='return'?COLORS.long:COLORS.short,symbol:kind==='return'?'circle':'diamond'},
              hovertemplate:'%{y}<br>%{x:.2f}'+(kind==='risk'?'% of book variance':'% per year')+'<extra></extra>'});
          });
        }
        graph.style.height=layout.height+'px';
        await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:false});
        windowLabel.hidden=view!=='window';
        windowLabel.textContent=(cfg.kind==='attribution-drawdowns'?'Selected-period P&L · ':cfg.kind==='attribution-years'?'Selected observations, annualized · ':'')+range[0]+' – '+range[1];
        host.querySelector('.blog-chart-status').hidden=true;host.querySelector('.blog-chart-fallback').hidden=true;
      } finally {busy=false;if(pending){pending=false;draw();}}
    }
    await draw();new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }
  function rankBars(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');
    ui.hidden=false;
    const chart=element('div','rank-metric-chart');
    chart.setAttribute('role','group');
    const plots=element('div','rank-metric-plots');
    const names=element('div','rank-metric-names');
    names.setAttribute('aria-hidden','true');
    for(const item of cfg.series)names.append(element('div','rank-metric-name',item.label));
    plots.append(names);
    chart.append(plots);
    ui.append(chart);
    const updates=cfg.metrics.map(metric=>{
      const [lower,upper]=metric.domain,span=upper-lower;
      const panel=element('div','rank-metric-panel');
      panel.setAttribute('role','group');
      panel.setAttribute('aria-label',metric.label);
      panel.style.setProperty('--zero',(-100*lower/span)+'%');
      panel.append(element('div','rank-metric-title',metric.label));
      const rows=cfg.series.map(item=>{
        const row=element('div','rank-metric-row');
        row.classList.toggle('rank-kumo',item.id.startsWith('kumo_'));
        const track=element('span','rank-metric-track');
        track.setAttribute('aria-hidden','true');
        const bar=element('span','rank-metric-bar'),number=element('span','rank-metric-value');
        track.append(bar);
        row.append(element('span','rank-metric-model',item.label),track,number);
        panel.append(row);
        return period=>{
          const value=period.values[item.id][metric.id];
          bar.style.left=(100*(Math.min(value,0)-lower)/span)+'%';
          bar.style.width=(100*Math.abs(value)/span)+'%';
          number.textContent=value.toFixed(metric.digits).replace('-','−');
        };
      });
      const axis=element('div','rank-metric-axis'),ticks=element('div','rank-metric-ticks');
      ticks.setAttribute('aria-hidden','true');
      ticks.append(element('span','rank-metric-zero','0'),element('span','rank-metric-max',String(upper)));
      axis.append(ticks);
      panel.append(axis);
      plots.append(panel);
      return period=>rows.forEach(update=>update(period));
    });

    function selectPeriod(index) {
      const period=cfg.periods[index];
      chart.setAttribute('aria-label','Rank metrics, '+period.label+', '+period.dates+' signal dates');
      updates.forEach(update=>update(period));
    }
    periodChoices(ui,cfg.periods.map(item=>item.label),selectPeriod);
    selectPeriod(0);
    host.querySelector('.blog-chart-status').hidden=true;
    host.querySelector('.blog-chart-fallback').hidden=true;
  }
  async function decileProfiles(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');
    ui.hidden=false;
    let period=cfg.periods[0];
    periodChoices(ui,cfg.periods.map(item=>item.label),index=>{period=cfg.periods[index];draw();});
    const modelKey=element('div'),graph=element('div','blog-chart-plot');
    ui.append(modelKey,graph);
    const visible=new Map(cfg.series.map(item=>[item.id,true]));
    sharedSeriesKey(modelKey,cfg.series,visible,draw,'Models to show');

    async function draw() {
      const stacked=host.clientWidth<580,dark=isDark(),height=stacked?650:275;
      const ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      const shown=cfg.series.filter(item=>visible.get(item.id)),traces=[];
      const layout={height,margin:{l:43,r:9,t:25,b:57},
        font:{family:'Bricolage Grotesque, sans-serif',size:11.5,color:ink},
        paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),
        showlegend:false,dragmode:false,hovermode:'closest',
        annotations:[],
      };
      cfg.metrics.forEach((metric,index)=>{
        const suffix=index?String(index+1):'',x='x'+suffix,y='y'+suffix;
        const xDomain=stacked?[0,1]:[index*.35,index*.35+.30];
        const yDomain=stacked?[(2-index)*.355,(2-index)*.355+.29]:[0,1];
        const values=cfg.periods.flatMap(item=>cfg.series.flatMap(s=>item.values[s.id][metric.id]));
        const lower=Math.min(...values),upper=Math.max(...values),padding=(upper-lower||1)*.09;
        layout['xaxis'+suffix]={domain:xDomain,anchor:y,tickvals:stacked?cfg.deciles:[1,3,5,7,10],
          range:[.6,10.4],showticklabels:!stacked||index===cfg.metrics.length-1,fixedrange:true,showgrid:false};
        layout['yaxis'+suffix]={domain:yDomain,anchor:x,range:[lower-padding,upper+padding],
          tickformat:metric.format,nticks:4,fixedrange:true,gridcolor:grid,zerolinecolor:COLORS.comparison};
        layout.annotations.push({text:metric.label,xref:'paper',yref:'paper',x:xDomain[0],y:yDomain[1],yshift:5,
          xanchor:'left',yanchor:'bottom',showarrow:false,font:{size:12,color:ink}});
        for(const item of shown) {
          traces.push({type:'scatter',mode:'lines',name:item.label,x:cfg.deciles,y:period.values[item.id][metric.id],
            xaxis:x,yaxis:y,line:{color:COLORS[item.role],width:1.8},
            hovertemplate:'Decile %{x}<br>'+metric.label+' %{y:'+metric.format+'}<extra>'+item.label+'</extra>'});
        }
      });
      layout.annotations.push({text:shown.length?'Score decile (1 = lowest)':'Select a model to show',
        xref:'paper',yref:'paper',x:.5,y:shown.length?0:.5,yshift:shown.length?-42:0,showarrow:false,font:{size:12}});
      graph.style.height=height+'px';
      await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:false});
    }

    await draw();
    host.querySelector('.blog-chart-status').hidden=true;
    host.querySelector('.blog-chart-fallback').hidden=true;
    new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;
    new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }
  // Small fixed comparisons: hover exposes estimates and their observed ranges.
  async function panels(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const inPeriod=refitPeriod(ui,cfg.panels.flatMap(p=>p.x),Number(host.dataset.refitSplit),draw);
    const graph=element('div','blog-chart-plot');ui.append(graph);
    async function draw() {
      const narrow=host.clientWidth<550,cols=host.clientWidth<300?1:2,rows=Math.ceil(cfg.panels.length/cols);
      const dark=document.documentElement.dataset.theme==='dark',ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      const height=rows*(narrow?134:145)+44;
      graph.style.height=height+'px';
      const layout={autosize:true,height,margin:{l:32,r:9,t:21,b:38},showlegend:false,
        font:{family:'Bricolage Grotesque, sans-serif',size:narrow?11:12,color:ink},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),annotations:[],shapes:[]},traces=[];
      const panels=cfg.panels.map(panel=>{
        const indices=panel.x.flatMap((year,i)=>inPeriod(year)?[i]:[]);
        if(indices.length===panel.x.length)return panel;
        const rows=values=>indices.map(i=>values[i]);
        const x=rows(panel.x),ticks=(panel.ticks||x).filter(inPeriod);
        return {...panel,x,y:rows(panel.y),low:panel.low&&rows(panel.low),high:panel.high&&rows(panel.high),
          ticks:ticks.length>=2?ticks:x};
      });
      const xValues=panels.flatMap(p=>p.x),xLow=Math.min(...xValues),xHigh=Math.max(...xValues),xPad=(xHigh-xLow||1)*.06;
      if(cfg.sharedX)layout.annotations.push({text:cfg.sharedX,x:.5,y:0,yshift:-27,xref:'paper',yref:'paper',showarrow:false});
      panels.forEach((p,i)=>{
        const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix,col=i%cols,row=Math.floor(i/cols);
        const xd=cols===1?[0,1]:col===0?[0,.43]:[.58,1];
        const yd=[1-(row+1)/rows+.09/rows,1-row/rows-.08/rows];
        if(row&&cfg.sharedX)yd[1]-=.18/rows;
        const comparable=cfg.panels.filter(q=>q.title===p.title).flatMap(q=>[...q.y,...q.low||[],...q.high||[]]);
        const lo=Math.min(...comparable),hi=Math.max(...comparable),pad=(hi-lo||1)*.1;
        layout['xaxis'+suffix]={domain:xd,anchor:y,showgrid:false,zeroline:false,title:{text:cfg.sharedX?'':p.xTitle,font:{size:12}},tickvals:p.ticks||p.x,
          range:cfg.sharedX?[xLow-xPad,xHigh+xPad]:undefined,showticklabels:!cfg.sharedX||row===rows-1};
        const domain=p.domain?[Math.min(p.domain[0],lo-pad),Math.max(p.domain[1],hi+pad)]:[p.zero?Math.min(0,lo-pad):lo-pad,hi+pad];
        layout['yaxis'+suffix]={domain:yd,anchor:x,gridcolor:grid,zeroline:false,tickvals:p.yTicks,tickformat:p.format||'',range:domain};
        if(Number.isFinite(p.reference))layout.shapes.push({type:'line',xref:x+' domain',x0:0,x1:1,yref:y,y0:p.reference,y1:p.reference,line:{color:COLORS.comparison,width:1,dash:'dot'},layer:'below'});
        layout.annotations.push({text:p.title,x:xd[0],y:yd[1]+.01,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false});
        traces.push({type:'scatter',mode:'lines+markers',x:p.x,y:p.y,xaxis:x,yaxis:y,
          line:{color:COLORS.comparison,width:1.3},marker:{color:p.x.map(v=>v===p.selected?COLORS.long:COLORS.comparison),size:p.x.map(v=>v===p.selected?8:4.5),symbol:p.x.map(v=>v===p.selected?'diamond':'circle')},
          error_y:p.low?{type:'data',symmetric:false,array:p.high.map((v,j)=>v-p.y[j]),arrayminus:p.y.map((v,j)=>v-p.low[j]),color:COLORS.comparison,thickness:1,width:3}:undefined,
          customdata:p.low?p.x.map((_,j)=>[p.low[j],p.high[j]]):undefined,
          hovertemplate:(p.xTitle||'Setting')+': %{x}<br>'+p.title+': %{y:.3f}'+(p.low?'<br>Schedule range: %{customdata[0]:.3f}–%{customdata[1]:.3f}':'')+'<extra></extra>'});
      });
      await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:false});
    }
    await draw();host.querySelector('.blog-chart-status').hidden=true;host.querySelector('.blog-chart-fallback').hidden=true;
    new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }
  async function calendarDistribution(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    let periods=cfg.periods;
    periodChoices(ui,['Both periods',...cfg.periods.map(p=>p.title)],index=>{
      periods=index?[cfg.periods[index-1]]:cfg.periods;draw();
    });
    const graph=element('div','blog-chart-plot');ui.append(graph);
    async function draw() {
      const mobile=host.clientWidth<550,dark=isDark(),ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      const height=mobile&&periods.length>1?416:245,traces=[],layout={autosize:true,height,
        margin:{l:mobile?76:87,r:12,t:28,b:48},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),
        font:{family:'Bricolage Grotesque, sans-serif',size:mobile?11:12,color:ink},hoverlabel:hoverStyle(),
        dragmode:false,showlegend:false,hovermode:'closest',
        annotations:[{text:'Annualized net return (%)',x:.5,y:0,yshift:-24,xref:'paper',yref:'paper',
          showarrow:false,yanchor:'top',font:{size:12}}]};
      graph.style.height=height+'px';
      const weekdays=['Monday','Tuesday','Wednesday','Thursday','Friday'];
      const labels=['One book','Two books','Three books'];
      for(const [i,period] of periods.entries()) {
        const s=i?String(i+1):'',x='x'+s,y='y'+s;
        const xd=mobile||periods.length===1?[0,1]:[i*.54,i*.54+.46],yd=mobile&&periods.length>1?(i?[0,.42]:[.58,1]):[0,1];
        layout['xaxis'+s]={domain:xd,anchor:y,range:period.limits,tick0:0,dtick:1,fixedrange:true,
          gridcolor:grid,zeroline:false};
        layout['yaxis'+s]={domain:yd,anchor:x,range:[-.48,2.48],tickvals:[2,1,0],ticktext:labels,
          fixedrange:true,showgrid:false,zeroline:false,showticklabels:mobile||i===0};
        layout.annotations.push({text:period.title,x:xd[0],y:yd[1],yshift:5,xref:'paper',yref:'paper',
          showarrow:false,xanchor:'left',yanchor:'bottom',font:{size:13}});
        for(const count of [1,2,3]) {
          const points=period.points.filter(point=>point.sleeves===count);
          const values=points.map(point=>point.annual_return),row=3-count;
          const color=count===3?(dark?'#76bda5':'#176b58'):COLORS.short;
          traces.push({type:'scatter',mode:'lines',x:[Math.min(...values),Math.max(...values)],y:[row,row],
            xaxis:x,yaxis:y,line:{color,width:1.3},opacity:.55,hoverinfo:'skip'});
          traces.push({type:'scatter',mode:'markers',x:values,y:points.map(point=>point.position),xaxis:x,yaxis:y,
            marker:{size:6,color,line:{color:plotSurface(),width:.55}},
            customdata:points.map(point=>weekdays[point.weekday-1]+' · '+(count===1?'week ':'weeks ')+point.schedules.replaceAll('+',', ')),
            hovertemplate:'%{customdata}<br>%{x:.2f}% annualized net return<extra></extra>'});
        }
      }
      await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:false});
    }
    await draw();host.querySelector('.blog-chart-status').hidden=true;host.querySelector('.blog-chart-fallback').hidden=true;
    new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }
  Object.assign(api,{load,plotly,whenVisible,periodChoices});
  function init() {document.querySelectorAll('.blog-chart').forEach(host=>whenVisible(host,()=>mount(host)));}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof window==='undefined'?globalThis:window);
