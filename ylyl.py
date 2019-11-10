import basc_py4chan
import requests
import os
import sqlite3
from datetime import datetime

def get_yl(section):
    board = basc_py4chan.Board(section)
    all_thread_ids = board.get_all_thread_ids()    
    conn = sqlite3.connect("/home/ubuntu/project/example.db")

    # print("contents before:")
    # for row in conn.execute("select id, threadid, date, files, downloaded, section, active from threads"):        
    #     print(row)

    for thread_id in all_thread_ids:     
        thread = board.get_thread(thread_id)
        try:
            topic = thread.topic
        except:
            continue

        thecomment = str(topic.comment)
        thesubject = str(topic.subject)

        if "YLYL" in thesubject or "ylyl" in thesubject or "Ylyl" in thesubject or "YLYL" \
            in thecomment or "ylyl" in thecomment or "Ylyl" in thecomment:
            
            yl_record = []
            yl_record.append(thread_id)                     #the thread id
            yl_record.append(topic.datetime)                    #the date
            numfiles = 0            
            for f in thread.file_objects():
                numfiles+=1
            yl_record.append(numfiles)                      #number of files
            yl_record.append(0)                             #how many downloaded
            yl_record.append(section)                             #which section
            yl_record.append(1)                             #set thread active
     
            threadexists = 0  # doest not exist in db

            for row in conn.execute("select exists(select 1 from threads where threadid is (?))", [thread_id]):     
                threadexists = row[0] 

            if threadexists == 0:
                try:
                    with conn:
                        conn.execute("insert into threads(threadid, date, files, downloaded, section, active) \
                        values (?, ?, ?, ?, ?, ?)", yl_record)
                except sqlite3.IntegrityError:
                        print("ERROR")    
            else:
                try:
                    with conn:
                        conn.execute("update threads set files = (?) \
                        where threadid is (?)", (yl_record[2],yl_record[0]))
                except sqlite3.OperationalError:
                    print("error...updating thread")   
           
    # print("contents after lurking:")
    # for row in conn.execute("select id, threadid, date, files, downloaded, section, active from threads"):        
    #     print(row)

    conn.close()

def initdb():    
    conn = sqlite3.connect("/home/ubuntu/project/example.db")
    try:
        with conn:
            conn.execute('''create table threads (id integer primary key AUTOINCREMENT,\
                threadid integer unique, date datetime, files integer , downloaded integer, section integer, active integer)''')
    except sqlite3.OperationalError:
        print("table exists")
    conn.close()

def fetchall_yl(section):
    conn = sqlite3.connect("/home/ubuntu/project/example.db") 
    board = basc_py4chan.Board(section)
    listofactivethreads = []
    print("list of active threads")
    
    for row in conn.execute("select id, threadid, date, files, downloaded, section, active from threads \
    where active is 1 and section is (?)", [section]): 
        listofactivethreads.append(row)
        print(row)
       
    
    for activethread in listofactivethreads:
        thread = board.get_thread(activethread[1])
        prev_downloaded = activethread[4]    
        downloaded = 0
        try:
            for f in thread.file_objects():     
                if downloaded >= prev_downloaded:
                    # download the files

                    dest_dir = "/home/ubuntu/project/" + section + "/" + str(activethread[1]) + "/"
                    dest_exact = dest_dir + f.filename

                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    r = requests.get(f.file_url)

                    with open(dest_exact, 'wb') as f:  
                        f.write(r.content)

                    prev_downloaded+=1          
                downloaded+=1
        except:
            print("inactive: ", activethread[1])
            conn.execute("update threads set active = (?) \
            where threadid is (?)", (0, activethread[1]))
              
        try:
            with conn:
                conn.execute("update threads set downloaded = (?) \
                where threadid is (?)", (downloaded, activethread[1]))
                # print("downloaded" , downloaded)
        except sqlite3.OperationalError:
            print("error...updating thread")   


    # print("contents after download:")
    # for row in conn.execute("select id, threadid, date, files, downloaded, section, active from threads"):        
    #     print(row)

    conn.close()


initdb()
get_yl("b")
fetchall_yl("b")

get_yl("gif")
fetchall_yl("gif")