const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const charts=require('../assets/js/blog-charts.js');
const vm=require('node:vm');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/low-volatility-sizing/performance.json')));
const returns=id=>data.series.find(s=>s.id===id).values.map(v=>v/data.scale);
const episodes=JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/low-volatility-sizing/episodes.json')));
const episodeReturns=id=>episodes.series.find(s=>s.id===id).values.map(v=>v/episodes.scale);

test('deferred charts start once near the viewport and work without an observer',async()=>{
  for(const supported of [true,false]) {
    let notify,starts=0;
    const classes=new Set(),host={classList:{add:c=>classes.add(c),remove:c=>classes.delete(c)}};
    const document={readyState:'complete',querySelectorAll:()=>[]},window={document};
    if(supported)window.IntersectionObserver=class {
      constructor(callback){notify=callback;}observe(){}unobserve(){}
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/js/blog-charts.js'),'utf8'),{window,document});
    window.BlogCharts.whenVisible(host,()=>{starts++;});
    if(supported) {
      notify([{target:host,isIntersecting:false}]);assert.equal(starts,0);
      notify([{target:host,isIntersecting:true}]);notify([{target:host,isIntersecting:true}]);
    }
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(starts,1);assert.equal(classes.has('chart-pending'),false);
  }
});

test('fixed-notional P&L rebases additively, including its drawdown',()=>{
  assert.deepEqual(charts.additivePath([0,.1,-.2,.05],0,3),{equity:[0,10,-10,-5],drawdown:[0,0,-20,-15]});
  assert.deepEqual(charts.additivePath([0,.1,-.2,.05],1,3),{equity:[0,-20,-15],drawdown:[0,-20,-15]});
});

test('non-overlapping attribution totals reconcile daily for every leg',()=>{
  const read=name=>JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/portfolio-attribution/'+name)));
  const theme=read('interactive-themes.json'),legs=read('interactive-legs.json');
  assert.deepEqual(theme.dates,legs.dates);
  const all=new Map([...theme.series,...legs.series].map(s=>[s.id,s.values]));
  for(const leg of ['total','long','short'])for(let i=0;i<theme.dates.length;i++) {
    const sum=theme.charts.themes.series.reduce((total,key)=>total+all.get(leg+'_'+key)[i],0);
    assert.ok(Math.abs(sum-all.get(leg+'_book')[i])<=6,'Reconciliation failed at '+theme.dates[i]);
  }
});

test('regime bars preserve the original classifications and rounded figures',()=>{
  const read=name=>JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/portfolio-attribution/'+name)));
  const theme=read('interactive-themes.json'),original=read('themes.json');
  for(const [key,label] of [['declines','Declines'],['rallies','Strong rallies']]) {
    const mask=theme.charts.regimes.masks[key],n=mask.reduce((a,b)=>a+b,0);
    for(const s of theme.series)if(s.id.startsWith('total_')&&original.regimes[label][s.label]!==undefined) {
      const annual=s.values.reduce((sum,v,i)=>sum+v*mask[i],0)/theme.scale/n*252*100;
      assert.ok(Math.abs(annual-original.regimes[label][s.label])<.006,s.label);
    }
  }
});

test('a selected window excludes the return into its opening close',()=>{
  const values=[0,.1,-.2,.05];
  assert.deepEqual(charts.path(values,1,3).equity,[100,80,84]);
  assert.ok(Math.abs(charts.path(values,1,3).drawdown[1]+.2)<1e-14);
  assert.equal(charts.stats([.1]),null);
  assert.equal(charts.stats([0,0]).sharpe,null);
});

test('the three displayed Table 1 rows survive export at published precision',()=>{
  for(const [id,expected] of [
    ['strategy',['6.8','9.8','0.72','-38.0']],
    ['equal',['-3.3','33.4','0.07','-87.8']],
    ['hedged',['8.0','24.5','0.44','-68.2']]]) {
    const s=charts.stats(returns(id).slice(1));
    assert.deepEqual([(s.annual_return*100).toFixed(1),(s.volatility*100).toFixed(1),s.sharpe.toFixed(2),(s.drawdown*100).toFixed(1)],expected);
  }
});

test('both rally book contributions reconcile to total growth',()=>{
  for(const [a,b,loss,market] of [['1998-10-08','2000-03-09',-38,52],['2025-04-03','2026-05-27',-12,39]]) {
    const first=episodes.dates.indexOf(a),last=episodes.dates.indexOf(b),gross=episodeReturns('gross');
    const equity=charts.path(gross,first,last).equity;
    const long=charts.linked(episodeReturns('long'),gross,first,last),short=charts.linked(episodeReturns('short'),gross,first,last);
    equity.forEach((v,i)=>assert.ok(Math.abs(v-100-long[i]-short[i])<1e-6));
    assert.equal(Math.round(equity.at(-1)-100),loss);
    assert.equal(Math.round(charts.path(episodeReturns('index'),first,last).equity.at(-1)-100),market);
  }
});

test('display sampling preserves full-window endpoints and extreme losses',()=>{
  const values=charts.path(returns('equal'),0,data.dates.length-1);
  const indices=charts.displayIndices(data.dates,[values.equity,values.drawdown]);
  assert.equal(indices[0],0);assert.equal(indices.at(-1),data.dates.length-1);
  assert.equal(Math.min(...indices.map(i=>values.drawdown[i])),Math.min(...values.drawdown));
  assert.ok(indices.length<data.dates.length);
});
