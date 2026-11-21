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
    blend:['#365e79','#8cbdd5']};
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

  function stats(values, annualization=252) {
    if (values.length < 2) return null;
    let growth=1, peak=1, dd=0;
    const mean=values.reduce((a,b)=>a+b,0)/values.length;
    const vol=Math.sqrt(values.reduce((a,b)=>a+(b-mean)**2,0)/(values.length-1)*annualization);
    for (const r of values) {
      if (!Number.isFinite(r) || r <= -1) throw new Error('Invalid return');
      growth*=1+r; peak=Math.max(peak,growth); dd=Math.min(dd,growth/peak-1);
    }
    return {annual_return:Math.expm1(Math.log(growth)*annualization/values.length),
      volatility:vol, sharpe:vol ? mean*annualization/vol : null, drawdown:dd};
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

  const api={COLORS,signedColorScale,stats,path,narrowGrowthTicks,linked,additivePath,displayIndices};
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
  function segments(parent,label) {
    const group=element('div','blog-chart-segments');group.setAttribute('role','group');group.setAttribute('aria-label',label);
    parent.append(group);return group;
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
  // Window and period presets. Returns mark(range,custom), which presses the preset the chart shows:
  // the one clicked if it still applies, else the last matching one. Full resets a custom view, so it
  // never shows as pressed while that view is on.
  function rangePresets(parent,full,episodes,current,apply,visiblePeriods=null) {
    const presets=[],clamp=([a,b])=>[a<full[0]?full[0]:a,b>full[1]?full[1]:b];let chosen=null;
    function add(group,label,target,isCustom=true) {
      const button=element('button','',label),preset={button,target,isCustom};button.type='button';
      button.onclick=()=>{chosen=preset;apply(...target(),isCustom);};group.append(button);presets.push(preset);
    }
    const windows=segments(controlRow(parent,'Window'),'Window length');
    for(const years of [1,3,5]) add(windows,years+'Y',()=>{
      const end=current()[1],d=new Date(end+'T00:00:00Z');d.setUTCFullYear(d.getUTCFullYear()-years);return clamp([d.toISOString().slice(0,10),end]);});
    if(!visiblePeriods)add(windows,'Full',()=>[...full],false);
    if(episodes?.length) {
      const periods=visiblePeriods||segments(controlRow(parent,'Periods'),'Periods');
      if(visiblePeriods)add(periods,'Full history',()=>[...full],false);
      for(const [label,a,b] of episodes) add(periods,label,()=>clamp([a,b]));
    }
    return (range,custom=false)=>{
      const shows=preset=>{const [a,b]=preset.target();return a===range[0]&&b===range[1]&&(preset.isCustom||!custom);};
      const pressed=chosen&&shows(chosen)?chosen:presets.filter(shows).at(-1);
      for(const preset of presets)preset.button.setAttribute('aria-pressed',String(preset===pressed));
    };
  }
  function format(value,percent=false) {
    return value===null || !Number.isFinite(value) ? '—' :
      (percent ? (value*100).toFixed(1)+'%' : value.toFixed(2));
  }

  // Fixed matrices share typography, theme handling and loading with time series.
  async function matrix(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
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
      await Plotly.react(graph,[{type:'heatmap',x:cfg.columns,y:indices.map(String),z:indices.map(i=>cfg.values[i]),
        zmin:-limit,zmax:limit,colorscale:signedColorScale(),
        xgap:1,ygap:1,customdata:indices.map(i=>cfg.columns.map(()=>cfg.descriptions[i])),
        hovertemplate:'%{customdata}<br>%{x}: %{z:.3f}<extra></extra>',
        colorbar:{orientation:'h',thickness:8,len:mobile?.85:.5,x:.5,xanchor:'center',y:-Math.max(.12,40/(height-90)),yanchor:'top',
          tickvals:[-limit,0,limit],tickformat:'.2f',tickangle:0,outlinewidth:0,title:{text:cfg.unit,side:'top',font:{size:12}}}}],
        {height,margin:{l:10,r:10,t:10,b:80},font:{family:'Bricolage Grotesque, sans-serif',size:12,color:dark?'#dce3eb':'#27343d'},
          paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),
          xaxis:{type:'category',tickangle:0,tickvals:mobile?[cfg.columns[0],cfg.columns[Math.floor(cfg.columns.length/2)],cfg.columns.at(-1)]:cfg.columns},
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
      const [data]=await Promise.all([load(host.dataset.source),plotly()]);
      if(data.version!==1) throw new Error('Unsupported chart version');
      const cfg=data.charts[host.dataset.chart], bars=['bars','grouped-bars'].includes(cfg.kind);
      if(cfg.kind==='matrix'){await matrix(host,cfg);return;}
      if(cfg.kind==='panels'){await panels(host,cfg);return;}
      if(cfg.kind==='calendar-distribution'){await calendarDistribution(host,cfg);return;}
      if(cfg.kind.startsWith('attribution')){await attribution(host,data,cfg);return;}
      const all=new Map(data.series.map(s=>[s.id,{...s,returns:s.values.map(v=>v/data.scale)}]));
      const series=cfg.series.map(id=>all.get(id));
      const full=[cfg.start||data.dates[0],cfg.end||data.dates.at(-1)];
      const openingRange=cfg.initialRange||full;
      let range=[...openingRange], ready=false, busy=false, pending=false;
      const visible=new Map(series.map(s=>[s.id,s.visible!==false && (s.role!=='index'||cfg.benchmark===true)]));
      const optionalBoxes=new Map();
      let legendTimer;
      const ui=host.querySelector('.blog-chart-ui'); ui.hidden=false;
      if(cfg.heading)ui.append(element('p','blog-chart-heading',cfg.heading));
      const visiblePeriods=host.dataset.visiblePeriods&&cfg.episodes?.length?segments(ui,'Chart period'):null;
      if(visiblePeriods)visiblePeriods.classList.add('blog-chart-periods');
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
      // The opening close sets the base. Label the years in which returns accrue.
      const episodes=visiblePeriods ? cfg.episodes.map(([label,opening,end])=>{
        const firstReturn=data.dates.find(date=>date>opening && date<=end);
        if(!firstReturn)return [label,opening,end];
        const endDate=new Date(end+'T00:00:00Z');
        const lastLabel=endDate.getUTCMonth()===11 ? end.slice(0,4) :
          endDate.toLocaleDateString('en',{month:'short',year:'numeric',timeZone:'UTC'});
        return [firstReturn.slice(0,4)+'–'+lastLabel,opening,end];
      }) : cfg.episodes;
      const markPresets=rangePresets(extra,full,episodes,()=>range,setRange,visiblePeriods);
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
      if(benchmark) benchmarkBox=checkbox(bars?benchmark.label:'Market',visible.get(benchmark.id),value=>{visible.set(benchmark.id,value);draw();});
      for(const s of series.filter(s=>s!==benchmark&&(s.visible===false||cfg.showLegend===false)))optionalBoxes.set(s.id,
        checkbox(s.label,visible.get(s.id),value=>{visible.set(s.id,value);draw();}));
      const graph=element('div','blog-chart-plot');ui.append(graph);
      const windowLabel=element('p','blog-chart-window');windowLabel.setAttribute('aria-live','polite');ui.append(windowLabel);
      if(cfg.controlsBelow)windowLabel.after(extra);
      const statisticsPanel=element('details','blog-chart-statistics');statisticsPanel.open=cfg.statisticsOpen??false;
      statisticsPanel.append(element('summary','','Window statistics'));ui.append(statisticsPanel);
      const tableWrap=element('div','blog-chart-table-wrap'); statisticsPanel.append(tableWrap);
      const table=element('table');tableWrap.append(table);
      table.setAttribute('aria-label','Selected-window statistics');
      const head=element('thead'),hr=element('tr');head.append(hr);table.append(head);
      ['Series',cfg.additive?'Annual P&L / return':'Annual growth','Volatility','Sharpe','Max drawdown'].forEach(label=>{const th=element('th','',label);th.scope='col';hr.append(th);});
      const body=element('tbody');table.append(body);
      statisticsPanel.append(element('p','blog-chart-note',cfg.note));
      if(cfg.kind==='values'||cfg.statistics===false)statisticsPanel.hidden=true;
      function updateTable(first,last) {
        body.replaceChildren();
        for(const s of series.filter(s=>visible.get(s.id)&&!s.contribution)) {
          const m=stats(s.returns.slice(first+(bars?0:1),last+1),data.annualization);
          if(m&&s.additive) {
            const values=s.returns.slice(first+1,last+1);
            m.annual_return=values.reduce((a,b)=>a+b,0)/values.length*data.annualization;
            m.drawdown=Math.min(...additivePath(s.returns,first,last).drawdown)/100;
          }
          const row=element('tr'),label=element('th','',bars&&s.id.startsWith('decile_')?'Decile '+s.label:s.label);label.scope='row';row.append(label);
          for(const key of ['annual_return','volatility','sharpe','drawdown'])row.append(element('td','',m?(s.additive&&key==='drawdown'?(m[key]*100).toFixed(1)+' pp':format(m[key],key!=='sharpe')):'—'));
          body.append(row);
        }
        if(!body.children.length) {const row=element('tr'),td=element('td','','Show a series in the legend to see its statistics.');td.colSpan=5;row.append(td);body.append(row);}
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
          if(first<0||last<=first) {
            windowLabel.hidden=false;
            windowLabel.textContent='Choose a window containing at least two observations.';
            body.replaceChildren();graph.hidden=true;return;
          }
          graph.hidden=false;
          const dates=data.dates.slice(first,last+1),t=theme(),traces=[];
          const mobile=host.clientWidth<550;
          const plotHeight=visiblePeriods?mobile?425:470:bars?430:cfg.drawdown||cfg.contributions?405:300;
          const layout={autosize:true,height:plotHeight,
            margin:{l:mobile?44:50,r:12,t:bars?26:cfg.showLegend===false?25:mobile?69:57,b:33},font:{family:'Bricolage Grotesque, sans-serif',size:mobile?11.5:12,color:t.text},
            paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),hovermode:bars?'closest':'x unified',
            modebar:{color:t.text,bgcolor:'rgba(0,0,0,0)',activecolor:COLORS.strategy},
            dragmode:'zoom',showlegend:cfg.showLegend!==false,legend:{orientation:'h',y:1.10,yanchor:'bottom',x:0,font:{size:mobile?11:12},groupclick:'togglegroup'},
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
              const ticks=[];for(let exponent=-3;exponent<8;exponent++)for(const n of [1,2,5])ticks.push(n*10**exponent);
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
              heading(cfg.drawdown?(cfg.additive?'Drawdown (points)':'Drawdown (%)'):'Linked book contributions (pp)',.29,8);
            }
            for(const s of series) {
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
            if(cfg.directLabels&&traces.some(tr=>tr.yaxis!=='y2'&&tr.visible===true)) {
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
          updateTable(first,last);
          windowLabel.hidden=cfg.showWindow===false||(!cfg.showWindow&&range[0]===openingRange[0]&&range[1]===openingRange[1]);
          windowLabel.textContent=dates[0]+' – '+dates.at(-1);
          windowLabel.title=cfg.showLegend===false?'Choose series under Explore.':'Click a legend entry to toggle; double-click to isolate.';
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
              const a=data.dates.findIndex(d=>d>=range[0]);let b=data.dates.length-1;while(data.dates[b]>range[1])b--;
              updateTable(a,b);
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
    const full=[data.dates[0],data.dates.at(-1)];let range=[...full],leg='total',custom=false,busy=false,pending=false;
    let focus=cfg.focus||null;
    const expanded=new Set(focus?[focus]:[]),componentControls=new Map();
    const from=element('input'),to=element('input');from.type=to.type='date';
    for(const [input,value] of [[from,full[0]],[to,full[1]]]){input.min=full[0];input.max=full[1];input.value=value;}
    function setRange(a,b,isCustom=true){if(a>b)return;range=[a<full[0]?full[0]:a,b>full[1]?full[1]:b];from.value=range[0];to.value=range[1];custom=isCustom;markPresets(range,custom);draw();}
    from.onchange=to.onchange=()=>{if(from.value&&to.value)setRange(from.value,to.value);};
    const markPresets=rangePresets(extra,full,cfg.episodes,()=>range,setRange);
    dateRange(controlRow(extra,'Dates'),from,to);
    markPresets(range,custom);
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
        for(const [key,{wrap,box}] of componentControls){wrap.hidden=!!focus;box.checked=expanded.has(key);}
        const keys=(focus?[focus]:cfg.series).filter(k=>cfg.kind==='attribution'||k!=='cost').flatMap(k=>expanded.has(k)?(cfg.kind==='attribution-years'?cfg.components[k]:[k,...cfg.components[k]]):[k]);
        if(cfg.kind==='attribution-regimes'&&!focus)keys.unshift('book');
        const nested=k=>[...expanded].some(parent=>cfg.components[parent].includes(k));
        const shown=keys.map(k=>all.get(leg+'_'+k));
        const ids=indices(...range),traces=[];
        const layout={autosize:true,margin:{l:mobile?145:160,r:20,t:45,b:45},
          font:{family:'Bricolage Grotesque, sans-serif',size:12,color:ink},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),showlegend:false,annotations:[],barmode:'overlay'};
        function title(text,x,y){layout.annotations.push({text,x,y,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false,font:{size:12}});}
        if(cfg.kind==='attribution-years') {
          const cols=mobile?2:3,rows=Math.ceil(shown.length/cols);layout.height=rows*(mobile?185:190)+50;layout.margin={l:40,r:10,t:35,b:30};
          const years=[...new Set(ids.map(i=>data.dates[i].slice(0,4)))];
          shown.forEach((s,i)=>{
            const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix,col=i%cols,row=Math.floor(i/cols);
            const xd=[col/cols+.02,(col+1)/cols-.05],yd=[1-(row+1)/rows+.25/rows,1-row/rows-.14/rows];
            const values=years.map(year=>metric(s,ids.filter(j=>data.dates[j].startsWith(year)),'return'));
            layout['xaxis'+suffix]={domain:xd,anchor:y,type:'linear',showgrid:false,zeroline:false,tickmode:'linear',dtick:years.length>10?10:years.length>5?5:1};
            layout['yaxis'+suffix]={domain:yd,anchor:x,range:[-11.7,11.7],tickvals:[-10,0,10],gridcolor:grid,zerolinecolor:grid};
            title(mobile?s.label.replace('Medium- and long-term','Med./long-term'):s.label,xd[0],yd[1]+.01);
            traces.push({type:'bar',x:years.map(Number),y:values.map(v=>Math.max(-10,Math.min(10,v))),customdata:values,
              marker:{color:values.map(v=>v<0?COLORS.short:COLORS.long)},xaxis:x,yaxis:y,hovertemplate:s.label+' · %{x}<br>%{customdata:.2f}% a year<extra></extra>'});
            const clipped=values.flatMap((v,j)=>Math.abs(v)>10?[j]:[]);
            traces.push({type:'scatter',mode:'markers',x:clipped.map(j=>Number(years[j])),y:clipped.map(j=>Math.sign(values[j])*10.5),
              marker:{symbol:clipped.map(j=>values[j]>0?'triangle-up':'triangle-down'),size:6,color:clipped.map(j=>values[j]>0?COLORS.long:COLORS.short)},
              xaxis:x,yaxis:y,customdata:clipped.map(j=>values[j]),hovertemplate:'%{customdata:.2f}% a year<extra></extra>'});
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
            : (custom?[range]:cfg.windows).map(([a,b])=>[custom?'Selected window':a.slice(0,4)+'–'+b.slice(2,4),indices(a,b,null,true)]);
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
          const specs=[['Return (% a year)',ids,'return'],['Share of book risk (%)',ids,'risk']];
          const cols=mobile?1:specs.length,rows=mobile?specs.length:1;
          layout.height=rows*(shown.length*26+(mobile?140:90));
          specs.forEach(([label,ix,kind],i)=>{
            const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix,values=shown.map(s=>metric(s,ix,kind));
            const xd=mobile?[0,1]:[i/cols+.02,(i+1)/cols-.08],yd=mobile?[1-(i+1)/rows+.22/rows,1-i/rows-.10/rows]:[0,1];
            const lo=Math.min(0,...values),hi=Math.max(0,...values),pad=(hi-lo||1)*.12;
            layout['xaxis'+suffix]={domain:xd,anchor:y,range:[lo-pad,hi+pad],gridcolor:grid,zerolinecolor:grid,nticks:4};
            layout['yaxis'+suffix]={domain:yd,anchor:x,type:'category',autorange:'reversed',tickvals:shown.map(s=>s.label),
              ticktext:shown.map((s,j)=>nested(keys[j])?'↳ '+s.label:cfg.components[keys[j]]?'<b>'+s.label+'</b>':s.label),showticklabels:mobile||i===0,automargin:true};
            title(label,xd[0],yd[1]+.02);
            if(!ix.length)title('No observations in this window',xd[0],(yd[0]+yd[1])/2);
            traces.push({type:'bar',orientation:'h',x:values,y:shown.map(s=>s.label),xaxis:x,yaxis:y,
              marker:{color:values.map(v=>v<0?COLORS.short:COLORS.long),opacity:keys.map(k=>nested(k)?.8:1)},
              hovertemplate:'%{y}<br>%{x:.2f}'+(kind==='total'?' points':kind==='risk'?'% of book variance':'% a year')+'<extra></extra>'});
          });
        }
        graph.style.height=layout.height+'px';
        await Plotly.react(graph,traces,layout,{responsive:true,displayModeBar:false});
        windowLabel.hidden=!custom;
        windowLabel.textContent=(cfg.kind==='attribution-drawdowns'?'Selected-period P&L · ':cfg.kind==='attribution-years'?'Selected observations, annualized · ':'')+range[0]+' – '+range[1];
        host.querySelector('.blog-chart-status').hidden=true;host.querySelector('.blog-chart-fallback').hidden=true;
      } finally {busy=false;if(pending){pending=false;draw();}}
    }
    await draw();new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    let width=host.clientWidth;new ResizeObserver(()=>{if(width!==host.clientWidth){width=host.clientWidth;draw();}}).observe(host);
  }
  // Small fixed comparisons: hover exposes estimates and their observed ranges.
  async function panels(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const graph=element('div','blog-chart-plot');ui.append(graph);
    async function draw() {
      const narrow=host.clientWidth<550,cols=host.clientWidth<300?1:2,rows=Math.ceil(cfg.panels.length/cols);
      const dark=document.documentElement.dataset.theme==='dark',ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      const height=rows*(narrow?134:145)+44;
      graph.style.height=height+'px';
      const layout={autosize:true,height,margin:{l:32,r:9,t:21,b:38},showlegend:false,
        font:{family:'Bricolage Grotesque, sans-serif',size:narrow?11:12,color:ink},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),hoverlabel:hoverStyle(),annotations:[],shapes:[]},traces=[];
      const xValues=cfg.panels.flatMap(p=>p.x),xLow=Math.min(...xValues),xHigh=Math.max(...xValues),xPad=(xHigh-xLow||1)*.06;
      if(cfg.sharedX)layout.annotations.push({text:cfg.sharedX,x:.5,y:0,yshift:-27,xref:'paper',yref:'paper',showarrow:false});
      cfg.panels.forEach((p,i)=>{
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
    const graph=element('div','blog-chart-plot');ui.append(graph);
    async function draw() {
      const mobile=host.clientWidth<550,dark=isDark(),ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      const height=mobile?416:245,traces=[],layout={autosize:true,height,
        margin:{l:mobile?76:87,r:12,t:28,b:48},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:plotSurface(),
        font:{family:'Bricolage Grotesque, sans-serif',size:mobile?11:12,color:ink},hoverlabel:hoverStyle(),
        dragmode:false,showlegend:false,hovermode:'closest',
        annotations:[{text:'Annualized net return (%)',x:.5,y:0,yshift:-24,xref:'paper',yref:'paper',
          showarrow:false,yanchor:'top',font:{size:12}}]};
      graph.style.height=height+'px';
      const weekdays=['Monday','Tuesday','Wednesday','Thursday','Friday'];
      const labels=['One book','Two books','Three books'];
      for(const [i,period] of cfg.periods.entries()) {
        const s=i?String(i+1):'',x='x'+s,y='y'+s;
        const xd=mobile?[0,1]:[i*.54,i*.54+.46],yd=mobile?(i?[0,.42]:[.58,1]):[0,1];
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
  Object.assign(api,{load,plotly,whenVisible});
  function init() {document.querySelectorAll('.blog-chart').forEach(host=>whenVisible(host,()=>mount(host)));}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof window==='undefined'?globalThis:window);
