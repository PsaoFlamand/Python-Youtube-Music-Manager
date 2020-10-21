import re
import tkinter as tk
import threading
import tkinter.scrolledtext as tkst
import requests
import youtube_dl
from tkinter.ttk import Progressbar
import multiprocessing
import subprocess
import time

class App(tk.Tk): 

    def __init__(self, *args, **kwargs):

        #Standard setup

        tk.Tk.__init__(self, *args, **kwargs) 
        self.title('SammaSounds')
        self.configure(bg='light grey')         
        self.minsize(width=500, height=120)
        self.maxsize(width=500, height=120)

        #Implement Widgets
        
        self.txt0 = tk.Label(self, text="Search for Music:",bg='light grey')
        self.txt0.grid(row=0, column=0, sticky='w')
        self.txtin0 = tk.Entry(self,width=45) 
        self.txtin0.grid(row=0,column=0, sticky='n')
        self.button0 = tk.Button(self, text="Search", command=self.threadstarter) 
        self.button0.grid(row=0,column=0,sticky='e')
        self.lstbox0 = tk.Listbox(self,width=77,height=5) 
        self.lstbox0.bind("<Double-Button-1>", self.selector) 
        self.lstbox0.grid(row=1,column=0,sticky='nsw') 
        self.scroll0 = tk.Scrollbar(self, orient="vertical") 
        self.scroll0.config(command=self.lstbox0.yview) 
        self.scroll0.grid(row=1,column=1,sticky='nsw')
        self.lstbox0.config(yscrollcommand=self.scroll0.set)
        self.p = Progressbar(self,orient='vertical',length=90,mode="determinate",takefocus=True,maximum=5)
        self.p.grid(row=1,column=2)
        
    def threadstarter(self):
        try:
            proc.stop()
            proc = multiprocessing.Process(target=self.searcher(), args=())
            proc.start()
        except:
            proc = multiprocessing.Process(target=self.searcher(), args=())
            proc.start()
    def searcher(self):
       
        #Retrieve url and name results from search query
        self.update()
        self.lstbox0.delete(0, tk.END)
        excess = self.txtin0.get() 
        excess=re.sub(' ','+',excess)
        link='https://www.youtube.com/results?search_query='+ excess
        self.urlresults=[]
        self.nameresults=[]
        a6=0
        combined=''
        a9=0
        for i in requests.get(link):
            self.update()
            if a9==1: #attach neighbor in case of incomplete chunk
                combined=combined+str(i)
                print(combined,"\n")
                m = re.search('"videoIds"', str(combined))
                s0=str(combined)[m.end():]
                s0 = s0.split(',')
                s0="".join(s0[0])
                s0=re.sub('[\]\[}"\':]','',s0)

                if len(s0)==11: #youtube video ID must be 11 chars long
                    a6+=1

                    self.urlresults.append('https://www.youtube.com/watch?v='+s0)
                    self.urlresults = list(dict.fromkeys(self.urlresults))
                    if len(self.urlresults)==5:#Limit search results to 5
                        break
                combined=''
                a9=0
            if re.search('"videoIds"',str(i)):

                combined=combined+str(i)
                a9=1
        a2=0
        a3=0
        combined=''
        while  1:
            if a2==5:
                break
            for i2 in self.urlresults:
                if a2==5:
                    break
                self.update()

                for i3 in requests.get(i2):
                    if a3==1:#May be an incomplete chunk, add its neighbor
                        self.p.step()
                        combined=combined+str(i3)
                        m = re.search(''',"title":"''', str(combined))
                        
                        s1=str(combined)[m.end():]
                        s1 = s1.split(',')
                        s1="".join(s1[0])
                        s1=re.sub(' ','_',s1)
                        s1=re.sub('[\W]','',s1)
                        s1=re.sub('_',' ',s1)
                        self.lstbox0.insert(a2,str(s1))
                        self.nameresults.append(str(s1))
                        a3=0
                        a2+=1
                        if a2==5:
                            break
                        combined=''

                    if re.search(''',"title":"''',str(i3)):

                        combined=combined+str(i3)
                        a3=1
                    
                  
                self.update()

    def selector(self,event):
        #Launch start of download of selected file
        widget = event.widget 
        selection=widget.curselection() 
        words = widget.get(selection[0]) 
        words=words.split(' ')
        selection=re.sub("\D", "", str(selection))
        thread1 = threading.Thread(target=self.download(selection))
     
        thread1.start()
        words='' 

    def download(self,choice):
        #download and strip audio
        pick=self.urlresults[int(choice)]
        subprocess.Popen('youtube-dl -x --audio-format mp3 '+ pick)

        
if __name__ == "__main__": 

        app = App() 
        app.mainloop() 
