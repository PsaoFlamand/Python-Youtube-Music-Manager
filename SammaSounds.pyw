import re
import tkinter as tk
import threading
import tkinter.scrolledtext as tkst
import requests
import youtube_dl
from tkinter.ttk import Progressbar
import multiprocessing

class App(tk.Tk): 

    def __init__(self, *args, **kwargs):

        #Standard setup

        tk.Tk.__init__(self, *args, **kwargs) 
        self.title('SammaSounds')
        self.configure(bg='light grey')         
        self.minsize(width=530, height=270)
        self.maxsize(width=530, height=270)

        #Implement Widgets
        
        self.txt0 = tk.Label(self, text="Search for Music:",bg='light grey')
        self.txt0.grid(row=0, column=0, sticky='w')
        self.txtin0 = tk.Entry(self,width=45) 
        self.txtin0.grid(row=0,column=0, sticky='n')
        self.button0 = tk.Button(self, text="Search", command=self.threadstarter) 
        self.button0.grid(row=0,column=0,sticky='e')
        self.lstbox0 = tk.Listbox(self,width=80,height=15) 
        self.lstbox0.bind("<Double-Button-1>", self.selector) 
        self.lstbox0.grid(row=1,column=0,sticky='nsw') 
        self.scroll0 = tk.Scrollbar(self, orient="vertical") 
        self.scroll0.config(command=self.lstbox0.yview) 
        self.scroll0.grid(row=1,column=1,sticky='nsw')
        self.lstbox0.config(yscrollcommand=self.scroll0.set)
        self.p = Progressbar(self,orient='vertical',length=240,mode="determinate",takefocus=True,maximum=95500)
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
        for i in requests.get(link):
            self.update()

            if re.search('"videoIds"',str(i)):#"url"
                m = re.search('"videoIds"', str(i))
                s0=str(i)[m.end():]
                s0 = s0.split(',')
                s0="".join(s0[0])
                s0=re.sub('[\]\[}"\':]','',s0)

                if len(s0)==11: #youtube video ID must be 11 chars long

                    self.urlresults.append('https://www.youtube.com/watch?v='+s0)
                    self.urlresults = list(dict.fromkeys(self.urlresults))
        a2=0
        a3=0
        combined=''
        for i2 in self.urlresults:
            self.update()
            
            for i3 in requests.get(i2):
                self.p.step()            
                
                if a3==1:#If an incomplete chunk is recieved, add its neighbor
                    combined=combined+str(i3)
                    m = re.search(''',"title":"''', str(combined))
                    
                    s1=str(combined)[m.end():]
                    s1 = s1.split(',')
                    s1="".join(s1[0])
                    s1=re.sub(' ','_',s1)
                    s1=re.sub('[\W]','',s1)
                    s1=re.sub('_',' ',s1)
                    self.lstbox0.insert(a2,str(s1))
                    a3=0
                    a2+=1
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
        thread1=threading.Thread(target=self.download(selection))
        thread1.start()
        words='' 

    def download(self,choice):
        #download and strip audio
        pick=self.urlresults[int(choice)]
        ydl_opts = {'loglevel':'quiet',
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192', }],}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([pick])
        
if __name__ == "__main__": 

        app = App() 
        app.mainloop() 
