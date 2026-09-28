/* Shared static chart renderer. Daily observations remain authoritative. */
(function (root) {
  'use strict';
  const COLORS = Object.freeze({strategy:'#376da4', comparison:'#8997a5', hedged:'#c47a26',
    long:'#248577', short:'#bd6045', index:'#78669b', cash:'#7e825a',
    low_risk:'#376da4', low_volatility:'#248577', beta:'#b89147',
    market:'#78669b', size:'#ac6986', liquidity:'#5e8c8d', momentum:'#aa703e',
    reversal:'#bf684e', short_interest:'#458f70', sector:'#85835b', residual:'#7c7e87'});

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

  function path(values, first, last) {
    let growth=100, peak=100;
    const equity=[100], drawdown=[0];
    for (let i=first+1;i<=last;i++) {
      growth*=1+values[i]; peak=Math.max(peak,growth);
      equity.push(growth); drawdown.push(growth/peak-1);
    }
    return {equity,drawdown};
  }

  function linked(values, parent, first, last) {
    let growth=1, contribution=0;
    const result=[0];
    for (let i=first+1;i<=last;i++) {
      contribution+=growth*values[i]; growth*=1+parent[i]; result.push(contribution*100);
    }
    return result;
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

  const api={COLORS,stats,path,linked,displayIndices};
  if (typeof module!=='undefined') module.exports=api;
  root.BlogCharts=api;
  if (!root.document) return;
  const documents=new Map();
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
  function format(value,percent=false) {
    return value===null || !Number.isFinite(value) ? '—' :
      (percent ? (value*100).toFixed(1)+'%' : value.toFixed(2));
  }

  // Fixed matrices share typography, theme handling and loading with time series.
  async function matrix(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const graph=element('div','blog-chart-plot');ui.append(graph);
    graph.style.height='420px';
    async function draw() {
      const dark=document.documentElement.dataset.theme==='dark',mobile=host.clientWidth<550;
      const limit=Math.max(...cfg.values.flat().map(Math.abs));
      await Plotly.react(graph,[{type:'heatmap',x:cfg.columns,y:cfg.rows,z:cfg.values,
        zmin:-limit,zmax:limit,colorscale:[[0,COLORS.short],[.5,dark?'#252c34':'#f6f6f4'],[1,COLORS.strategy]],
        xgap:2,ygap:2,customdata:cfg.descriptions.map(label=>cfg.columns.map(()=>label)),
        hovertemplate:'%{customdata}<br>%{x}: %{z:.3f}<extra></extra>',
        colorbar:{orientation:'h',thickness:8,len:.5,x:1,xanchor:'right',y:-.12,outlinewidth:0,title:{text:cfg.unit,font:{size:12}}}}],
        {height:420,margin:{l:10,r:10,t:10,b:80},font:{family:'Bricolage Grotesque, sans-serif',size:12,color:dark?'#dce3eb':'#27343d'},
          paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
          xaxis:{type:'category',tickangle:0,tickvals:mobile?cfg.columns.filter((_,i)=>i%2===0):cfg.columns},
          yaxis:{autorange:'reversed',automargin:true}}, {responsive:true,displayModeBar:false});
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
      const all=new Map(data.series.map(s=>[s.id,{...s,returns:s.values.map(v=>v/data.scale)}]));
      const series=cfg.series.map(id=>all.get(id));
      const full=[cfg.start||data.dates[0],cfg.end||data.dates.at(-1)];
      let range=cfg.initialRange||[...full], ready=false, busy=false, pending=false;
      const visible=new Map(series.map(s=>[s.id,s.visible!==false && (s.role!=='index'||cfg.benchmark===true)]));
      const optionalBoxes=new Map();
      let relative=false,relativeBox,legendTimer;
      const ui=host.querySelector('.blog-chart-ui'); ui.hidden=false;
      if(cfg.heading)ui.append(element('p','blog-chart-heading',cfg.heading));
      const extra=element('details','blog-chart-options');
      extra.append(element('summary','','Explore'));ui.append(extra);
      const controls=element('div','blog-chart-controls'); extra.append(controls);
      const start=element('input'),end=element('input'); start.type=end.type='date';
      start.setAttribute('aria-label','Start date'); end.setAttribute('aria-label','End date');
      [start,end].forEach(input=>{input.min=full[0];input.max=full[1];});
      function setRange(a,b) {
        if(a>b || b<full[0] || a>full[1]) {start.value=range[0];end.value=range[1];return;}
        range=[a<full[0]?full[0]:a,b>full[1]?full[1]:b]; draw();
      }
      for(const years of [1,3,5]) {
        const button=element('button','',years+'Y'); button.type='button'; controls.append(button);
        button.onclick=()=>{const d=new Date(range[1]+'T00:00:00Z');d.setUTCFullYear(d.getUTCFullYear()-years);setRange(d.toISOString().slice(0,10),range[1]);};
      }
      const reset=element('button','','Full'); reset.type='button';reset.onclick=()=>setRange(...full);controls.append(reset);
      const episodes=element('div','blog-chart-controls');extra.append(episodes);
      for(const [label,a,b] of cfg.episodes||[]) {
        const button=element('button','',label); button.type='button';button.onclick=()=>setRange(a,b);episodes.append(button);
      }
      const dates=element('div','blog-chart-controls');
      const startLabel=element('label','','From '),endLabel=element('label','','to ');
      startLabel.append(start);endLabel.append(end);dates.append(startLabel,endLabel);extra.append(dates);
      start.onchange=end.onchange=()=>{if(start.value&&end.value)setRange(start.value,end.value);};
      let benchmarkBox;
      const benchmark=series.find(s=>s.role==='index');
      function checkbox(label,checked,change,container=dates) {
        const wrap=element('label'),box=element('input'); box.type='checkbox';box.checked=checked;
        box.onchange=()=>change(box.checked);wrap.append(box,document.createTextNode(' '+label));container.append(wrap);return box;
      }
      if(benchmark) benchmarkBox=checkbox(bars?benchmark.label:'Market',visible.get(benchmark.id),value=>{visible.set(benchmark.id,value);draw();},controls);
      for(const s of series.filter(s=>s.visible===false))optionalBoxes.set(s.id,
        checkbox(s.label,false,value=>{visible.set(s.id,value);draw();},controls));
      if(cfg.relative&&benchmark) relativeBox=checkbox('Strategy / index',false,value=>{relative=value;draw();});
      const graph=element('div','blog-chart-plot');ui.append(graph);
      const windowLabel=element('p','blog-chart-window');windowLabel.setAttribute('aria-live','polite');ui.append(windowLabel);
      const statisticsPanel=element('details','blog-chart-statistics');statisticsPanel.open=cfg.statisticsOpen??false;
      statisticsPanel.append(element('summary','','Window statistics'));ui.append(statisticsPanel);
      const tableWrap=element('div','blog-chart-table-wrap'); statisticsPanel.append(tableWrap);
      const table=element('table');tableWrap.append(table);
      table.setAttribute('aria-label','Selected-window statistics');
      const head=element('thead'),hr=element('tr');head.append(hr);table.append(head);
      ['Series','Annual return','Volatility','Sharpe','Max drawdown'].forEach(label=>{const th=element('th','',label);th.scope='col';hr.append(th);});
      const body=element('tbody');table.append(body);
      statisticsPanel.append(element('p','blog-chart-note',cfg.note));
      if(cfg.kind==='values')statisticsPanel.hidden=true;
      function updateTable(first,last) {
        body.replaceChildren();
        for(const s of series.filter(s=>visible.get(s.id)&&!s.contribution)) {
          const m=stats(s.returns.slice(first+(bars?0:1),last+1),data.annualization);
          const row=element('tr'),label=element('th','',bars&&s.id.startsWith('decile_')?'Decile '+s.label:s.label);label.scope='row';row.append(label);
          for(const key of ['annual_return','volatility','sharpe','drawdown'])row.append(element('td','',m?format(m[key],key!=='sharpe'):'—'));
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
          start.value=range[0];end.value=range[1];
          const first=data.dates.findIndex(d=>d>=range[0]);
          let last=data.dates.length-1;while(last>=0&&data.dates[last]>range[1])last--;
          if(first<0||last<=first) {
            windowLabel.textContent='Choose a window containing at least two observations.';
            body.replaceChildren();graph.hidden=true;return;
          }
          graph.hidden=false;
          const dates=data.dates.slice(first,last+1),t=theme(),traces=[];
          const mobile=host.clientWidth<550;
          const layout={autosize:true,height:bars?540:cfg.drawdown||cfg.contributions?560:420,
            margin:{l:55,r:15,t:bars?35:mobile?100:75,b:45},font:{family:'Bricolage Grotesque, sans-serif',size:mobile?11:13,color:t.text},
            paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',hovermode:bars?'closest':'x unified',
            modebar:{color:t.text,bgcolor:'rgba(0,0,0,0)',activecolor:COLORS.strategy},
            dragmode:'zoom',showlegend:true,legend:{orientation:'h',y:1.16,yanchor:'bottom',x:0,font:{size:mobile?11:12},groupclick:'togglegroup'},
            xaxis:{type:bars?'category':'date',gridcolor:t.grid,showgrid:false,automargin:true},
            yaxis:{gridcolor:t.grid,zerolinecolor:t.grid,automargin:true},annotations:[]};
          const color=s=>COLORS[s.role]||COLORS.comparison;
          function trace(s,x,y,extra={}) {
            return {type:'scatter',mode:'lines',x,y,name:s.label,legendgroup:s.id,
              visible:visible.get(s.id)?true:'legendonly',showlegend:(s.role!=='index'&&s.visible!==false)||visible.get(s.id),
              line:{color:color(s),width:s.role==='index'?1.3:1.8,dash:s.dash||'solid'},
              hovertemplate:'%{x|%d %b %Y}<br>%{y:.2f}<extra>%{fullData.name}</extra>',...extra};
          }
          function heading(text,y) {layout.annotations.push({text,x:0,y,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false,font:{size:13,color:t.text}});}
          if(cfg.kind==='grouped-bars') {
            layout.height=360;layout.margin.t=65;layout.barmode='group';layout.bargap=.25;
            layout.yaxis.tickformat='.0%';layout.xaxis.title={text:'Decile (1 = lowest score)',font:{size:12}};
            heading('Annual return (%)',1);
            const groups=[...new Set(series.map(s=>s.group))];
            for(const group of groups) {
              const items=series.filter(s=>s.group===group);
              traces.push({type:'bar',name:group,legendgroup:items[0].id,
                x:items.map(s=>s.category),y:items.map(s=>stats(s.returns.slice(first,last+1),data.annualization)?.annual_return),
                visible:visible.get(items[0].id)?true:'legendonly',marker:{color:color(items[0])},
                hovertemplate:group+' · decile %{x}<br>%{y:.1%} a year<extra></extra>'});
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
            const secondary=cfg.drawdown||cfg.contributions;
            layout.xaxis.anchor=secondary?'y2':'y';
            layout.yaxis.domain=secondary?[.43,1]:[0,1];layout.yaxis.type=cfg.log?'log':'linear';
            if(cfg.growthRange&&range[0]===full[0]&&range[1]===full[1])layout.yaxis.range=cfg.growthRange;
            if(cfg.log) {
              const ticks=[];for(let exponent=-3;exponent<8;exponent++)for(const n of [1,2,5])ticks.push(n*10**exponent);
              layout.yaxis.tickmode='array';layout.yaxis.tickvals=ticks;layout.yaxis.ticktext=ticks.map(String);
            }
            heading(cfg.kind==='values'?cfg.unit:'Growth · 100 at selected start'+(cfg.log?' (log scale)':''),1);
            if(secondary) {
              layout.yaxis2={domain:[0,.29],anchor:'x',gridcolor:t.grid,zerolinecolor:t.grid,
                tickformat:cfg.drawdown?'.0%':'.0f',ticksuffix:cfg.contributions?' pp':''};
              if(cfg.contributionRange&&range[0]===full[0]&&range[1]===full[1])layout.yaxis2.range=cfg.contributionRange;
              heading(cfg.drawdown?'Drawdown (%)':'Linked book contributions (pp)',.29);
            }
            for(const s of series) {
              if(s.contribution) {
                const values=linked(s.returns,all.get(s.parent).returns,first,last);
                const indices=displayIndices(dates,[values]);
                traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values[i]),{yaxis:'y2',hovertemplate:'%{x|%d %b %Y}<br>%{y:.2f} pp<extra>%{fullData.name}</extra>'}));
              } else if(cfg.kind==='values') {
                traces.push(trace(s,dates,s.returns.slice(first,last+1)));
              } else {
                const values=path(s.returns,first,last),indices=displayIndices(dates,[values.equity,values.drawdown]);
                traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values.equity[i])));
                if(cfg.drawdown)traces.push(trace(s,indices.map(i=>dates[i]),indices.map(i=>values.drawdown[i]),{yaxis:'y2',showlegend:false,hovertemplate:'%{x|%d %b %Y}<br>%{y:.2%}<extra>%{fullData.name}</extra>'}));
              }
            }
            if(relative) {
              const a=path(all.get(cfg.relative).returns,first,last).equity,b=path(benchmark.returns,first,last).equity;
              const ratio=a.map((v,i)=>v/b[i]*100),indices=displayIndices(dates,[ratio]);
              traces.push({type:'scatter',mode:'lines',name:'Strategy / index',legendgroup:'relative',x:indices.map(i=>dates[i]),y:indices.map(i=>ratio[i]),line:{color:COLORS.strategy,dash:'dot'},hovertemplate:'%{y:.2f}<extra>Strategy / index</extra>'});
            }
            if(cfg.marker&&range[0]<=cfg.marker&&range[1]>=cfg.marker)layout.shapes=[{type:'line',xref:'x',yref:'paper',x0:cfg.marker,x1:cfg.marker,y0:0,y1:1,line:{color:t.text,width:1,dash:'dot'}}];
            if(cfg.band)layout.shapes=[{type:'rect',xref:'paper',yref:'y',x0:0,x1:1,y0:cfg.band[0],y1:cfg.band[1],fillcolor:t.grid,opacity:.4,line:{width:0},layer:'below'}];
          }
          await Plotly.react(graph,traces,layout,{responsive:true,displaylogo:false,scrollZoom:false,doubleClickDelay:300,
            modeBarButtonsToRemove:['select2d','lasso2d','autoScale2d'],toImageButtonOptions:{format:'svg',filename:'quant-notes-chart'}});
          updateTable(first,last);
          windowLabel.textContent=dates[0]+' – '+dates.at(-1);
          windowLabel.title='Click a legend entry to toggle; double-click to isolate.';
          if(benchmarkBox)benchmarkBox.checked=visible.get(benchmark.id);
          for(const [id,box] of optionalBoxes)box.checked=visible.get(id);
          if(relativeBox)relativeBox.checked=relative;
          if(!ready) {
            ready=true;
            graph.on('plotly_legendclick',event=>{
              clearTimeout(legendTimer);
              const id=graph.data[event.curveNumber].legendgroup;
              legendTimer=setTimeout(()=>{
                if(id==='relative')relative=false;
                else {const group=all.get(id)?.group,value=!visible.get(id);
                  for(const s of series)if(s.id===id||(group&&s.group===group))visible.set(s.id,value);}
                draw();},320);
              return false;
            });
            graph.on('plotly_legenddoubleclick',event=>{
              clearTimeout(legendTimer);
              const id=graph.data[event.curveNumber].legendgroup;
              const group=all.get(id)?.group;
              const isolated=series.filter(s=>visible.get(s.id)).every(s=>s.id===id||(group&&s.group===group))&&visible.get(id)&&!relative;
              for(const s of series)visible.set(s.id,isolated?(s.visible!==false&&(s.role!=='index'||cfg.benchmark===true)):(s.id===id||(group&&s.group===group)));
              relative=id==='relative';draw();return false;
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
              for(const s of series) {const tr=graph.data.find(t=>t.legendgroup===s.id);visible.set(s.id,tr.visible!==false&&tr.visible!=='legendonly');}
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
  // Small fixed comparisons: hover exposes estimates and their observed ranges.
  async function panels(host,cfg) {
    const ui=host.querySelector('.blog-chart-ui');ui.hidden=false;
    const graph=element('div','blog-chart-plot');ui.append(graph);
    async function draw() {
      const mobile=host.clientWidth<550,cols=mobile?1:2,rows=Math.ceil(cfg.panels.length/cols);
      const dark=document.documentElement.dataset.theme==='dark',ink=dark?'#dce3eb':'#27343d',grid=dark?'#36404a':'#e2e7eb';
      graph.style.height=(rows*240)+'px';
      const layout={autosize:true,height:rows*240,margin:{l:50,r:20,t:40,b:40},showlegend:false,
        font:{family:'Bricolage Grotesque, sans-serif',size:12,color:ink},paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',annotations:[]},traces=[];
      cfg.panels.forEach((p,i)=>{
        const suffix=i?String(i+1):'',x='x'+suffix,y='y'+suffix,col=i%cols,row=Math.floor(i/cols);
        const xd=[col/cols+.02,(col+1)/cols-.06],yd=[1-(row+1)/rows+.08,1-row/rows-.06];
        layout['xaxis'+suffix]={domain:xd,anchor:y,showgrid:false,title:{text:p.xTitle||'',font:{size:12}},tickvals:p.x};
        layout['yaxis'+suffix]={domain:yd,anchor:x,gridcolor:grid,zerolinecolor:grid,tickformat:p.format||'',rangemode:p.zero?'tozero':'normal'};
        layout.annotations.push({text:p.title,x:xd[0],y:yd[1]+.01,xref:'paper',yref:'paper',xanchor:'left',yanchor:'bottom',showarrow:false});
        traces.push({type:'scatter',mode:'lines+markers',x:p.x,y:p.y,xaxis:x,yaxis:y,
          line:{color:COLORS.comparison,width:1},marker:{color:p.x.map(v=>v===p.selected?COLORS.strategy:COLORS.comparison),size:p.x.map(v=>v===p.selected?9:6)},
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
  Object.assign(api,{load,plotly});
  function init() {document.querySelectorAll('.blog-chart').forEach(mount);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})(typeof window==='undefined'?globalThis:window);
