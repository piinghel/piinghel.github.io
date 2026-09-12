/* Daily accounting explorer: all series come from the verified saved fit. */
(() => {
  const root=document.getElementById('attribution-dynamics');
  if(!root)return;
  const episode=root.querySelector('.ad-episode'), factor=root.querySelector('.ad-factor');
  const slider=root.querySelector('.ad-slider'), status=root.querySelector('.ad-status');
  const panels=['.ad-exposure','.ad-payoff','.ad-pnl'].map(s=>root.querySelector(s));
  const ns='http://www.w3.org/2000/svg';
  const date=s=>Date.parse(s+'T00:00:00Z');
  const signed=(v,n=2)=>(v<0?'−':'+')+Math.abs(v).toFixed(n);
  const human=s=>new Date(date(s)).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'});
  function add(svg,tag,attrs,text){
    const el=document.createElementNS(ns,tag);
    for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);
    if(text!==undefined)el.textContent=text;
    svg.append(el);return el;
  }
  function extent(values){
    const min=Math.min(0,...values),max=Math.max(0,...values),raw=(max-min||1)/4;
    const magnitude=10**Math.floor(Math.log10(raw)),step=[1,2,5,10].find(n=>n*magnitude>=raw)*magnitude;
    const lo=Math.floor(min/step)*step,hi=Math.ceil(max/step)*step;
    return [lo===hi?lo-step:lo,lo===hi?hi+step:hi,step];
  }
  let data;
  const directions={beta:{sign:-1,name:'low beta',positive:'lower-beta stocks',negative:'higher-beta stocks'},
    volatility:{sign:-1,name:'low volatility',positive:'lower-volatility stocks',negative:'higher-volatility stocks'},
    momentum:{sign:1,name:'momentum',positive:'past winners',negative:'past losers'}};
  function oriented(rows,sign){return rows.map(row=>row.map((v,i)=>[1,2,3,4,6].includes(i)?sign*v:v));}
  function render(){
    if(!data)return;
    const direction=directions[factor.value];
    const e=data.episodes[Number(episode.value)],rows=oriented(e.factors[factor.value],direction.sign);
    const index=Math.min(Number(slider.value),rows.length-1), selected=rows[index];
    slider.max=rows.length-1;
    slider.setAttribute('aria-valuetext',human(selected[0]));
    root.querySelector('.ad-direction').textContent=`Positive ${direction.name} exposure favors ${direction.positive}; negative exposure favors ${direction.negative}.`;
    root.querySelector('.ad-exposure-title').textContent=`1. My exposure to ${direction.name} · units`;
    root.querySelector('.ad-pnl-title').textContent=`3. Portfolio P&L from ${direction.name} · cumulative points`;
    const series=[[[1,'--ad-long',''],[2,'--ad-short','5 3'],[3,'--ad-net','']],[[6,'--ad-net','']],[[7,'--ad-net','']]];
    const style=getComputedStyle(root);
    panels.forEach((svg,p)=>{
      svg.replaceChildren();
      const width=Math.max(280,svg.clientWidth),height=168,l=42,r=14,t=8,b=29;
      svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
      const minDate=date(e.peak),maxDate=date(e.end);
      const x=d=>l+(date(d)-minDate)/(maxDate-minDate)*(width-l-r);
      const limits=extent(rows.flatMap(row=>series[p].map(([col])=>row[col])));
      const pad=(limits[1]-limits[0])*.04;
      const y=v=>height-b-(v-limits[0]+pad)/(limits[1]-limits[0]+2*pad)*(height-t-b);
      add(svg,'rect',{x:l,y:t,width:x(e.low)-l,height:height-t-b,fill:style.getPropertyValue('--ad-grid'),opacity:.22});
      for(let v=limits[0];v<=limits[1]+limits[2]*.01;v+=limits[2]){
        add(svg,'line',{x1:l,x2:width-r,y1:y(v),y2:y(v),stroke:style.getPropertyValue('--ad-grid'),'stroke-width':.5});
        const digits=Math.max(0,-Math.floor(Math.log10(limits[2])));
        add(svg,'text',{x:l-7,y:y(v)+4,'text-anchor':'end'},(Math.abs(v)<limits[2]*.001?0:v).toFixed(digits).replace('-','−'));
      }
      add(svg,'line',{x1:l,x2:width-r,y1:y(0),y2:y(0),stroke:'currentColor',opacity:.35,'stroke-width':.7});
      for(const [col,color,dash] of series[p]){
        const initial=p===0?'':`M${l},${y(0)} `;
        const d=initial+rows.map((row,i)=>`${i===0&&!initial?'M':'L'}${x(row[0])},${y(row[col])}`).join(' ');
        add(svg,'path',{d,fill:'none',stroke:style.getPropertyValue(color),'stroke-width':col===3?1.8:1.3,'stroke-dasharray':dash});
        add(svg,'circle',{cx:x(selected[0]),cy:y(selected[col]),r:3,fill:style.getPropertyValue(color)});
      }
      add(svg,'line',{x1:x(e.low),x2:x(e.low),y1:t,y2:height-b,stroke:'currentColor','stroke-dasharray':'2 3',opacity:.4});
      add(svg,'line',{x1:x(selected[0]),x2:x(selected[0]),y1:t,y2:height-b,stroke:'currentColor',opacity:.6,'stroke-dasharray':'3 3'});
      for(const [d,anchor] of [[e.peak,'start'],[e.end,'end']]){
        const label=new Date(date(d)).toLocaleDateString('en-GB',{month:'short',year:'2-digit',timeZone:'UTC'});
        add(svg,'text',{x:x(d),y:height-6,'text-anchor':anchor},label);
      }
      const middle=rows[Math.floor(rows.length/2)][0];
      add(svg,'text',{x:x(middle),y:height-6,'text-anchor':'middle'},new Date(date(middle)).toLocaleDateString('en-GB',{month:'short',year:'2-digit',timeZone:'UTC'}));
    });
    root.querySelector('.ad-selected-date').textContent=`${human(selected[0])} · This day's ${direction.name} contribution`;
    root.querySelector('.ad-day-exposure').textContent=signed(selected[3],3);
    root.querySelector('.ad-day-return').textContent=signed(selected[4],3)+'%';
    root.querySelector('.ad-day-pnl').textContent=signed(selected[5],3)+' points';
  }
  function choose(){
    const e=data.episodes[Number(episode.value)],rows=e.factors[factor.value];
    slider.max=rows.length-1;
    slider.value=Math.max(0,rows.findIndex(r=>r[0]>e.low));render();
  }
  fetch(root.dataset.source).then(r=>{if(!r.ok)throw new Error('unavailable');return r.json();}).then(d=>{
    data=d;root.querySelector('.ad-content').hidden=false;status.hidden=true;choose();
    episode.addEventListener('change',choose);factor.addEventListener('change',choose);
    slider.addEventListener('input',render);
    for(const svg of panels){
      const inspect=event=>{
        const e=data.episodes[Number(episode.value)],rows=e.factors[factor.value];
        const box=svg.getBoundingClientRect(),fraction=Math.max(0,Math.min(1,(event.clientX-box.left-42)/(box.width-56)));
        const target=date(e.peak)+fraction*(date(e.end)-date(e.peak));
        slider.value=rows.reduce((best,row,i)=>Math.abs(date(row[0])-target)<Math.abs(date(rows[best][0])-target)?i:best,0);render();
      };
      svg.addEventListener('pointerdown',event=>{svg.setPointerCapture(event.pointerId);inspect(event);});
      svg.addEventListener('pointermove',event=>{if(svg.hasPointerCapture(event.pointerId))inspect(event);});
    }
    new ResizeObserver(render).observe(root);
    new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  }).catch(()=>{status.textContent='The daily explorer could not load. Please reload to try again; the surrounding figures show the episode totals.';});
})();
