// lee el arreglo PHOTOS o YEARS de una página de lugar y lo devuelve como JSON
const fs=require('fs');const f=process.argv[2];const s=fs.readFileSync(f,'utf8');
let m=s.match(/const (PHOTOS|YEARS)\s*=\s*\[/);if(!m){console.log('null');process.exit()}
let i=m.index+m[0].length-1,d=0,j=i,q=null,esc=false;
for(;j<s.length;j++){const c=s[j];
 if(q){if(esc){esc=false;continue}if(c==='\\'){esc=true;continue}if(c===q)q=null;continue}
 if(c==='"'||c==="'"||c==='`'){q=c;continue}
 if(c==='[')d++;else if(c===']'){d--;if(d===0)break}}
const txt=s.slice(i,j+1);
const val=(new Function('return '+txt))();
console.log(JSON.stringify({kind:m[1],data:val}));
