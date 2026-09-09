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
    let lo=Math.min(0,...values),hi=Math.max(0,...values),pad=(hi-lo||1)*.10;
    return [lo-pad,hi+pad];
  }
  let data;
  function render(){
    if(!data)return;
    const e=data.episodes[Number(episode.value)],rows=e.factors[factor.value];
    const index=Math.min(Number(slider.value),rows.length-1), selected=rows[index];
    slider.max=rows.length-1;
    slider.setAttribute('aria-valuetext',human(selected[0]));
    const all=data.episodes.flatMap(ep=>ep.factors[factor.value]);
    const series=[[[1,'--ad-long',''],[2,'--ad-short','5 3'],[3,'--ad-net','']],[[6,'--ad-net','']],[[7,'--ad-net','']]];
    const style=getComputedStyle(root);
    panels.forEach((svg,p)=>{
      svg.replaceChildren();
      const width=Math.max(280,svg.clientWidth),height=168,l=42,r=14,t=8,b=29;
      svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
      const minDate=date(e.peak),maxDate=date(e.end);
      const x=d=>l+(date(d)-minDate)/(maxDate-minDate)*(width-l-r);
      const limits=extent(all.flatMap(row=>series[p].map(([col])=>row[col])));
      const y=v=>height-b-(v-limits[0])/(limits[1]-limits[0])*(height-t-b);
      add(svg,'rect',{x:l,y:t,width:x(e.low)-l,height:height-t-b,fill:style.getPropertyValue('--ad-grid'),opacity:.22});
      for(let n=0;n<3;n++){
        const v=limits[0]+(limits[1]-limits[0])*n/2;
        add(svg,'line',{x1:l,x2:width-r,y1:y(v),y2:y(v),stroke:style.getPropertyValue('--ad-grid'),'stroke-width':.5});
        add(svg,'text',{x:l-7,y:y(v)+4,'text-anchor':'end'},v.toFixed(p===0?1:0).replace('-','−'));
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
    root.querySelector('.ad-readout').textContent=`${human(selected[0])} · ${selected[0]<=e.low?'Market-decline phase':'Market-recovery phase'}. Net exposure ${signed(selected[3],3)} × factor return ${signed(selected[4],3)}% = ${signed(selected[5],3)} P&L points today. Cumulative contribution: ${signed(selected[7])} points.`;
  }
  function choose(){
    const e=data.episodes[Number(episode.value)],rows=e.factors[factor.value];
    slider.value=Math.max(0,rows.findIndex(r=>r[0]>e.low));render();
  }
  fetch(root.dataset.source).then(r=>{if(!r.ok)throw new Error('unavailable');return r.json();}).then(d=>{
    data=d;root.querySelector('.ad-content').hidden=false;status.hidden=true;choose();
    episode.addEventListener('change',choose);factor.addEventListener('change',choose);
    slider.addEventListener('input',render);
    new ResizeObserver(render).observe(root);
    new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  }).catch(()=>{status.textContent='The daily explorer could not load. Please reload to try again; the surrounding figures show the episode totals.';});
})();

(() => {
  const select=document.getElementById('recovery-horizon');
  if(!select)return;
  const figure=document.getElementById('all-recoveries');
  const summaries={21:'shorts gained more in 9 / 11 episodes; median gap +2.73 points; net portfolio losses in 4 / 11.',
    63:'shorts gained more in 9 / 11 episodes; median gap +2.89 points; net portfolio losses in 4 / 11.',
    126:'shorts gained more in 3 / 11 episodes; median gap −2.49 points; net portfolio losses in 1 / 11.'};
  select.addEventListener('change',()=>{
    const horizon=select.value,suffix=horizon==='63'?'':'-'+horizon;
    for(const picture of figure.querySelectorAll('picture')){
      const dark=picture.classList.contains('theme-svg-figure--dark')?'_dark':'';
      picture.querySelector('img').src=`/assets/portfolio-attribution/recoveries${suffix}${dark}.svg?v=1`;
      picture.querySelector('img').alt=`All 11 ${horizon}-session recoveries: ${summaries[horizon]}`;
      picture.querySelector('source').srcset=`/assets/portfolio-attribution/recoveries${suffix}_mobile${dark}.svg?v=1`;
    }
    document.getElementById('recovery-caption-horizon').textContent=horizon;
    document.getElementById('recovery-summary').textContent=`${horizon} sessions: ${summaries[horizon]}`;
  });
})();
