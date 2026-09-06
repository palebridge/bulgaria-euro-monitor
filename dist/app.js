'use strict';
const $=id=>document.getElementById(id);
const make=(tag,text,className)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;};
const link=(text,url)=>{const a=make('a',text);a.href=url;return a;};
async function init(){
 try{
  const response=await fetch('snapshot.json');if(!response.ok)throw Error('Snapshot unavailable');const data=await response.json();
  for(const row of data.indicators){const card=make('article',undefined,'card');card.append(make('h3',row.label),make('div',row.value,'value'),make('p',row.period,'period'),make('p',row.note),link('Source ↗',data.sources[row.source].url));$('cards').append(card);}
  for(const source of data.sources){const li=make('li');li.append(link(source.title+' ↗',source.url));$('source-list').append(li);}
 }catch(e){$('cards').append(make('p','Research data could not load. Reload the page or use the source-data download.'));}
 try{
  const response=await fetch('series.json');if(!response.ok)throw Error('Feed unavailable');const data=await response.json();
  const entries=Object.entries(data.series||{});if(!entries.length)throw Error('No observations');
  const failures=entries.filter(([,s])=>s.error);$('feed-status').textContent='Last refresh attempt: '+data.attempted.slice(0,10)+(failures.length?' · '+failures.length+' feed(s) unavailable':'');
  if(failures.length)$('feed-status').classList.add('warning');
  for(const [key,s] of entries){const option=make('option',s.label);option.value=key;$('series').append(option);}
  const draw=()=>render(data.series[$('series').value]);$('series').addEventListener('change',draw);draw();
 }catch(e){$('feed-status').textContent='Automatic series unavailable. The dated research snapshot remains available.';$('feed-status').classList.add('warning');$('series').disabled=true;}
}
function render(s){
 $('series-meta').replaceChildren();$('chart').replaceChildren();$('observations').replaceChildren();
 const points=s.points||[];
 $('series-meta').append(document.createTextNode(s.unit+' · '+(s.fetched?'Retrieved '+s.fetched.slice(0,10):'No successful retrieval')+' · '),link('Eurostat source ↗',s.url));
 if(s.error)$('series-meta').append(make('p','Latest retrieval failed; any displayed observations are from the last successful retrieval.','warning'));
 if(!points.length){$('chart').append(make('p','No observations available for this series.'));return;}
 const latest=points[points.length-1];$('series-meta').append(make('p','Latest observation: '+latest.period+' · '+latest.value.toFixed(1)+'%'+(latest.flag?' · Flag: '+latest.flag:'')));
 const NS='http://www.w3.org/2000/svg';const el=(tag,attrs,text)=>{const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;return n;};
 const svg=el('svg',{viewBox:'0 0 940 320',role:'img','aria-label':s.label+'; exact values in the table below'});
 const min=Math.min(0,...points.map(p=>p.value)),max=Math.max(1,...points.map(p=>p.value)),span=max-min||1;
 const x=i=>65+i*835/Math.max(1,points.length-1),y=v=>260-(v-min)*220/span;
 for(let i=0;i<=4;i++){const v=min+span*i/4;svg.append(el('line',{x1:65,x2:900,y1:y(v),y2:y(v),stroke:'#dce5eb'}),el('text',{x:50,y:y(v)+5,'text-anchor':'end',fill:'#536b79','font-size':15},v.toFixed(1)));}
 const changeover=points.findIndex(p=>p.period>='2026');if(changeover>=0){svg.append(el('line',{x1:x(changeover),x2:x(changeover),y1:30,y2:260,stroke:'#8ca6b5','stroke-dasharray':'5 5'}),el('text',{x:Math.min(750,x(changeover)+8),y:20,fill:'#536b79','font-size':14},'Euro introduced · Jan 2026'));}
 svg.append(el('polyline',{points:points.map((p,i)=>x(i)+','+y(p.value)).join(' '),fill:'none',stroke:'#007b71','stroke-width':3}));
 points.forEach((p,i)=>{const dot=el('circle',{cx:x(i),cy:y(p.value),r:4,fill:'#007b71'});dot.append(el('title',{},p.period+': '+p.value+'%'));svg.append(dot);const tr=make('tr');tr.append(make('td',p.period),make('td',p.value.toFixed(1)+'%'),make('td',p.flag||'—'));$('observations').append(tr);});
 svg.append(el('text',{x:65,y:294,fill:'#536b79','font-size':15},points[0].period),el('text',{x:900,y:294,fill:'#536b79','font-size':15,'text-anchor':'end'},latest.period));$('chart').append(svg);
 $('series-meta').append(make('p','Source flags: p = provisional; e = estimated; b = break in series. Other flags are retained as published.','muted'));
}
init();
