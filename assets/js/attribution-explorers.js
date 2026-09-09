/* Explore the same saved observations behind the article's recovery totals. */
(() => {
  const byId=id=>document.getElementById(id);
  const recovery=byId('recovery-explorer'), stock=byId('stock-explorer');
  if(!recovery||!stock)return;
  const episode=byId('recovery-episode'), horizon=byId('recovery-horizon');
  const overview=byId('all-recoveries'), detail=byId('recovery-detail');
  const session=byId('recovery-session'), choice=byId('stock-choice'), stockSession=byId('stock-session');
  const signed=(v,n=2)=>(v<0?'−':'+')+Math.abs(v).toFixed(n);
  const human=s=>new Date(s+'T00:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'});
  const month=s=>new Date(s+'T00:00:00Z').toLocaleDateString('en-GB',{month:'short',year:'2-digit',timeZone:'UTC'});
  const summaries={21:'shorts gained more in 9 / 11 episodes; median gap +2.73 points; net portfolio losses in 4 / 11.',
    63:'shorts gained more in 9 / 11 episodes; median gap +2.89 points; net portfolio losses in 4 / 11.',
    126:'shorts gained more in 3 / 11 episodes; median gap −2.49 points; net portfolio losses in 1 / 11.'};
  let data;
  function add(svg,tag,attrs,text){
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [key,value] of Object.entries(attrs))el.setAttribute(key,value);
    if(text!==undefined)el.textContent=text;
    svg.append(el);
  }
  function bounds(values){
    const min=Math.min(0,...values),max=Math.max(0,...values);
    const raw=(max-min||1)/4, magnitude=10**Math.floor(Math.log10(raw));
    const step=[1,2,5,10].find(x=>x*magnitude>=raw)*magnitude;
    const lo=Math.floor(min/step)*step,hi=Math.ceil(max/step)*step;
    return {lo:lo===hi?lo-step:lo,hi:lo===hi?hi+step:hi,step};
  }
  function chart(svg,root,rows,series,values,index,{low,steps=false,recoveryDays=false}={}){
    if(!svg.clientWidth)return;
    const width=svg.clientWidth,height=168,left=44,right=12,top=9,bottom=29;
    const b=bounds(values),pad=(b.hi-b.lo)*.04;
    const x=i=>left+i/(rows.length-1)*(width-left-right);
    const y=v=>height-bottom-(v-b.lo+pad)/(b.hi-b.lo+2*pad)*(height-top-bottom);
    const style=getComputedStyle(root),color=key=>style.getPropertyValue(key).trim();
    svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
    if(low){
      const at=rows.findIndex(r=>r[0]===low);
      if(at>=0){
        add(svg,'rect',{x:left,y:top,width:x(at)-left,height:height-top-bottom,fill:color('--ad-grid'),opacity:.22});
        add(svg,'line',{x1:x(at),x2:x(at),y1:top,y2:height-bottom,stroke:'currentColor',opacity:.4,'stroke-dasharray':'2 3'});
      }
    }
    const digits=b.step<1?Math.max(0,-Math.floor(Math.log10(b.step))):0;
    for(let v=b.lo;v<=b.hi+b.step*.01;v+=b.step){
      add(svg,'line',{x1:left,x2:width-right,y1:y(v),y2:y(v),stroke:color('--ad-grid'),'stroke-width':.5});
      add(svg,'text',{x:left-7,y:y(v)+4,'text-anchor':'end'},v.toFixed(digits).replace('-','−'));
    }
    add(svg,'line',{x1:left,x2:width-right,y1:y(0),y2:y(0),stroke:'currentColor',opacity:.35,'stroke-width':.7});
    for(const [col,key,dash] of series){
      const d=rows.map((r,i)=>i===0?`M${x(i)},${y(r[col])}`:steps?`H${x(i)} V${y(r[col])}`:`L${x(i)},${y(r[col])}`).join(' ');
      add(svg,'path',{d,fill:'none',stroke:color(key),'stroke-width':1.6,'stroke-dasharray':dash||''});
      add(svg,'circle',{cx:x(index),cy:y(rows[index][col]),r:3,fill:color(key)});
    }
    add(svg,'line',{x1:x(index),x2:x(index),y1:top,y2:height-bottom,stroke:'currentColor',opacity:.5,'stroke-dasharray':'3 3'});
    for(const [i,anchor] of [[0,'start'],[Math.floor((rows.length-1)/2),'middle'],[rows.length-1,'end']]){
      add(svg,'text',{x:x(i),y:height-6,'text-anchor':anchor},recoveryDays?`Session ${i}`:month(rows[i][0]));
    }
  }
  function renderRecovery(){
    if(!data||episode.value==='all')return;
    const e=data.recoveries[Number(episode.value)],h=Number(horizon.value),rows=e.path.slice(0,h+1);
    const index=Math.min(Number(session.value),h),row=rows[index];
    const all=data.recoveries.flatMap(e=>e.path.slice(0,h+1));
    session.setAttribute('aria-valuetext',`Session ${index}, ${human(row[0])}`);
    chart(detail.querySelector('.ae-gains'),detail,rows,[[1,'--ad-long'],[2,'--ad-short','5 3']],all.flatMap(r=>[r[1],r[2]]),index,{recoveryDays:true});
    chart(detail.querySelector('.ae-books'),detail,rows,[[3,'--ad-long'],[4,'--ad-short','5 3'],[5,'--ad-net']],all.flatMap(r=>[r[3],r[4],r[5]]),index,{recoveryDays:true});
    byId('recovery-readout').textContent=index===0?`${human(row[0])} · Market low. All cumulative paths start at zero; the next session begins the measured recovery.`:
      `${human(row[0])} · Session ${index}. Stock gains: longs ${signed(row[1])}%, shorts ${signed(row[2])}% (gap ${signed(row[2]-row[1])} points). Actual P&L: longs ${signed(row[3])}, shorts ${signed(row[4])}, net ${signed(row[5])} points. Market since low: ${signed(row[6])}%. Beginning gross exposure today: longs ${row[7].toFixed(1)}%, shorts ${row[8].toFixed(1)}% of notional.`;
  }
  function updateRecovery(){
    const h=Number(horizon.value),isAll=episode.value==='all';
    overview.hidden=!isAll;detail.hidden=isAll;
    byId('recovery-caption-horizon').textContent=h;
    if(isAll){
      const suffix=h===63?'':'-'+h;
      for(const picture of overview.querySelectorAll('picture')){
        const dark=picture.classList.contains('theme-svg-figure--dark')?'_dark':'';
        picture.querySelector('img').src=`/assets/portfolio-attribution/recoveries${suffix}${dark}.svg?v=1`;
        picture.querySelector('img').alt=`All 11 ${h}-session recoveries: ${summaries[h]}`;
        picture.querySelector('source').srcset=`/assets/portfolio-attribution/recoveries${suffix}_mobile${dark}.svg?v=1`;
      }
      byId('recovery-summary').textContent=`${h} sessions: ${summaries[h]}`;
      byId('recovery-caption-view').textContent='Rows identify the market-low date; left shows stock gains and right shows actual net P&L.';
    }else if(data){
      const e=data.recoveries[Number(episode.value)];
      byId('recovery-summary').textContent=`Market low: ${human(e.low)} · ${h} sessions through ${human(e.path[h][0])}. Move the slider to inspect the path.`;
      byId('recovery-caption-view').textContent='Top: the changing books’ stock gains. Bottom: their actual portfolio contributions. A rising short-stock line means those stocks gained; it produces a loss on the short book below.';
      session.max=h;session.value=h;renderRecovery();
    }
  }
  function renderStock(){
    if(!data)return;
    const s=data.stocks[Number(choice.value)],rows=s.path,index=Number(stockSession.value),r=rows[index];
    const color=s.side==='short'?'--ad-short':'--ad-long';
    stockSession.setAttribute('aria-valuetext',human(r[0]));
    chart(stock.querySelector('.ae-weight'),stock,rows,[[1,color]],data.stocks.flatMap(s=>s.path.map(r=>r[1])),index,{low:s.low,steps:true});
    chart(stock.querySelector('.ae-stock-pnl'),stock,rows,[[2,color]],data.stocks.flatMap(s=>s.path.map(r=>r[2])),index,{low:s.low});
    byId('stock-readout').textContent=`${human(r[0])} · ${s.name}. ${Math.abs(r[1])<1e-10?'No position entering the session.':`${r[1]>0?'Long':'Short'} ${Math.abs(r[1]).toFixed(2)}% of notional entering the session.`} Cumulative actual P&L: ${signed(r[2],3)} points.`;
  }
  function chooseStock(){
    const rows=data.stocks[Number(choice.value)].path;
    stockSession.max=rows.length-1;stockSession.value=rows.findIndex(r=>r[0]==='2020-03-24');renderStock();
  }
  horizon.addEventListener('change',updateRecovery);
  episode.addEventListener('change',updateRecovery);
  fetch('/assets/portfolio-attribution/explorer-paths.json?v=1').then(r=>{
    if(!r.ok)throw new Error('Data unavailable');return r.json();
  }).then(d=>{
    data=d;
    d.recoveries.forEach((e,i)=>episode.add(new Option(human(e.low),String(i))));
    episode.disabled=false;
    d.stocks.forEach((s,i)=>choice.add(new Option(`${s.name} · ${s.side} at the low`,String(i))));
    choice.value=String(d.stocks.findIndex(s=>s.name==='Zscaler'));
    stock.querySelector('.ae-loading').hidden=true;stock.querySelector('.ae-content').hidden=false;
    session.addEventListener('input',renderRecovery);
    stockSession.addEventListener('input',renderStock);choice.addEventListener('change',chooseStock);
    byId('stock-examples').addEventListener('toggle',renderStock);
    const redraw=()=>{renderRecovery();renderStock();};
    new ResizeObserver(redraw).observe(recovery);new ResizeObserver(renderStock).observe(stock);
    new MutationObserver(redraw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    chooseStock();updateRecovery();
  }).catch(()=>{
    stock.querySelector('.ae-loading').textContent='The position examples could not load. Please reload to try again.';
    const note=document.createElement('p');note.className='figure-caption';
    note.textContent='Individual episode paths could not load. The all-episode comparison remains available.';
    recovery.append(note);
  });
})();
