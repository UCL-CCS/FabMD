# awk -f constraint.awk ../build/complex.pdb ../build/rec.pdb > cons.pdb
# using FIELDWIDTHS as it may not have space between occupancy and b-factor
# noting the format after using FIELDWIDTHS
BEGIN {
kbt=0.0019872041*300
pi2=3.14159*3.14159
FIELDWIDTHS = "6 5 5 4 2 4 12 8 8 6 6 12"
}
NR==FNR {
  p[NR]=$0; p1[NR]=$1; p3[NR]=$3; p4[NR]=$4; p6[NR]=$6; n1=NR;
  next
}
NR!=FNR {
  p3[NR]=$3; p4[NR]=$4; p6[NR]=$6; pf[NR]=$11; nt=NR;
  next
}
END {
   ff=8*kbt*pi2
   nres0=p6[n1+1]-1
   for(i=n1+1;i<=nt;i++) {
      p6[i]=p6[i]-nres0
      if(pf[i]!=0 && pf[i]!="      " && pf[i]!="") {
        if(p4[i]==" PD1") {
          fcon[p4[i],p3[i]]=ff/pf[i]
        } else if (p4[i]==" MG2") {
          fcon[p4[i],p3[i]]=ff/pf[i]
        } else {
          fcon[p6[i],p3[i]]=ff/pf[i]
        }
     }
   }
   for(i=1;i<=n1;i++) {
      p6[i]=p6[i]-0
      if(p4[i]==" PD1") {
        printf("%s%6.2f\n",substr(p[i],1,54),fcon[p4[i],p3[i]])
      } else if (p4[i]==" MG2") {
        printf("%s%6.2f\n",substr(p[i],1,54),fcon[p4[i],p3[i]])
      } else if (p1[i]~"^TER"||p1[i]~"^END") {
        printf("%s\n",p1[i])
      } else if (p4[i]==" WAT"||p4[i]==" HOH") {
        printf("%s%6.2f\n",substr(p[i],1,54),0.0)
      } else {
        printf("%s%6.2f\n",substr(p[i],1,54),fcon[p6[i],p3[i]])
      }
   }
}

