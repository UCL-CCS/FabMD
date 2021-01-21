function max(a,b) {if ((a+0.0) > (b+0.0)) return a; else return b;} 
function min(a,b) {if ((a+0.0) < (b+0.0)) return a; else return b;} 
BEGIN { 
} 
{  
 p[NR]=$1; n=NR;
} 
END { 
  # detemine xmax and xmin
  xmin=p[1]
  xmax=p[1]
  for(i=1;i<=n;i++) {
   xmax=max(xmax,p[i]);
   xmin=min(xmin,p[i]);
  }
  # print xmax-xmin
  printf("%10.5f %10.5f %10.5f\n",xmax,xmin,xmax-xmin);
}
