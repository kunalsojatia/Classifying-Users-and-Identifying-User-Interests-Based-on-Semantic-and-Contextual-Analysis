import pandas as pd  

df = pd.read_csv("beproject.csv")  
swdf = pd.read_csv("swearwords.csv")
swdf.head()





#####




count=0
counts=dict()
tcounts=dict()
 
for i,j,a,b in zip(df['user'],df['commentText'],df['replies.user'],df['replies.commentText']):
    if(type(j) is not float):
        k = j.split(' ')
        
        for l in k:
            if i in tcounts:
                tcounts[i]+=1
            else:
                tcounts[i]=1
            for m,n in zip(swdf['SLANGS'],swdf['WEIGHT']):
                
                if(type(l) is not int):
                    if (m.lower() == l.lower()):
                        if i in counts:
                            counts[i]+=n
                        else:
                            counts[i]=n  
            
    elif(type(b) is not float):        
        k = b.split(' ')
        
        for l in k:
            if a in tcounts:
                tcounts[a]+=1
            else:
                tcounts[a]=1
            for m,n in zip(swdf['SLANGS'],swdf['WEIGHT']):
                
                if(type(l) is not int):
                    if (m.lower() == l.lower()):
                        if a in counts:
                            counts[a]+=n
                        else:
                            counts[a]=n

for z in tcounts.keys():
    print(z)
    if z in counts.keys():
        print((counts[z]/tcounts[z])*100)
    else:
        print("NON-ABUSIVE")
    print()