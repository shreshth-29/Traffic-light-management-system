import os
path="C:\\Users\\Shreshth Mehrotra\\OneDrive\\Desktop\\Ariescodes\\kitti_single\\training\\label_2c"
l = os.listdir(path)
for p in range(len(l)-1,len(l)):
    
    testfile=l[p]
    linelist = open(path+"\\"+testfile).read().splitlines()
    names=['Car', 'Van', 'Truck','Pedestrian', 'Person_sitting', 'Cyclist', 'Tram','Misc','DontCare']
    N=[]
    for j in linelist:
        
        if(j[0] !="D"):
            m=j.split(" ")
            print(m)
            n=[]
            
            o=[]
            for i in range(4,8):
                n.append(float(m[i]))
                
            for k in range(0,len(names)-1):
                if(m[0]==names[k]):
                    o.append(k)
            
            left=n[0]
            top=n[3]
            right=n[2]
            bottom=n[1]
            xc=(left+right)/2
            yc=(top + bottom)/2
            wb=right-left
            hb=top-bottom
            width=1242

            height=375
            x=xc/width

            
            o.append(x)
            y=yc/height
            o.append(y)
            w=wb/width
            o.append(w)
            h=hb/height
            o.append(h)


            st=""
            for a in range(0,5):
                st=st+str(o[a])+" "
            st=st+"\n"
            N.append(st)
            print(o)
    print(N)
    npath="C:\\Users\\Shreshth Mehrotra\\OneDrive\\Desktop\\Ariescodes\\kitti_single\\training\\nlabel"
    file1 = open(npath+"\\"+testfile,'w')
    file1.writelines(N)
    file1.close()


        


