import speech_recognition as sr
import os 
import subprocess
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

d = '/Applications'
records = []
apps = os.listdir(d)
for app in apps:
    record = {}
    record['voice_command'] = 'open ' + app.split('.app')[0]
    record['sys_command'] = 'open ' + d +'/%s' %app.replace(' ','\ ')
    records.append(record)

##start python client 
es = Elasticsearch(['localhost:9200'])
bulk(es, records, index='voice_assistant', doc_type='text', raise_on_error=True)
##initialize speech recognizer and mic
r = sr.Recognizer()
mic = sr.Microphone()
startTime = time.time()
elapsedTime = 0

def say(text):
    subprocess.call(['say', text])


def search_es(query):
    res = es.search(index="voice_assistant", doc_type="text", body={                     
    "query" :{
        "match": {
            "voice_command": {
                "query": query,
                "fuzziness": 2
            }
            }
        },
    })
    return res['hits']['hits'][0]['_source']['sys_command']

def activate(phrase = 'hello jarvis'):
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            transcript = r.recognize_google(audio)
            if(transcript == 'thanks'):
                    os.system("ps -ef | grep jarvis.py | grep -v grep | awk '{print $2}' | xargs kill")
            if transcript.lower()==phrase:
                return True
            else:
                return False
    except:
        print("error")


def search_google(query):
    browser = webdriver.Chrome('/Users/dawsenrichins/Downloads/chromedriver')
    browser.get('http://www.google.com')
    search = browser.find_element_by_name('q')
    search.send_keys(query)
    search.send_keys(Keys.RETURN)



while True: 
    elapsedTime = time.time()-startTime
    print(elapsedTime)
    if(elapsedTime >= 20):
        os.system("ps -ef | grep jarvis.py | grep -v grep | awk '{print $2}' | xargs kill")
    if activate() == True:
        try:
            say("Yes Dawsen?")
            while True:
                with mic as source:
                    elapsedTime = time.time()-startTime
                    print(elapsedTime)
                    print("Say Something!")
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    transcript = r.recognize_google(audio)
                    print(transcript.lower())
                    googlePhrase = 'search google for '
                    if(transcript == 'thanks' or elapsedTime >= 20):
                        say("goodbye")
                        os.system("kill $(ps -ef | grep webdriver | grep -v grep | awk '{ print $2 }')")
                        os.system("ps -ef | grep jarvis.py | grep -v grep | awk '{print $2}' | xargs kill")
                        os.system("ps -ef | grep /Applications/Google Chrome.app | grep -v grep | awk '{print $2}' | xargs kill")
                        os.system("ps -ef | grep /Applications/Google Chrome.app/Contents/MacOS/Google | grep -v grep | awk '{print $2}' | xargs kill")
                        
                   
                    elif googlePhrase in transcript.lower():
                        search = transcript.lower().split(googlePhrase)[-1]
                        search_google(search)
                        say("I got these results for you")
                    
                    elif(transcript in ['what is my name', 'what do you call me', 'who is your master']):
                         say("Dawsen Richins")

                    else:
                        sys_command = search_es(transcript)
                        os.system(sys_command)
                        say("I opened that application for you")
                    
                    startTime = time.time()

        except:
            pass
    else:
        pass