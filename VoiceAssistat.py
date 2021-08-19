from __future__ import print_function
import time, playsound, os, pywhatkit, random
from pyjokes import get_jokes
import speech_recognition as sr
import pyttsx3, datetime, os.path, subprocess
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("listening...")
        audio = r.listen(source)
        said = ""
        print("wait!")

    try:
        said =r.recognize_google(audio)
        print(said)
        return said.lower()
    except:
        pass

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def google_auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

import pytz
def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.utc
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date')).split("+")[0]
            start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            end = event['end'].get('dateTime', event['end'].get('date')).split("T")[1].split("+")[0]
            end = datetime.datetime.strptime(end, '%H:%M:%S')
            event_date = start.strftime("%d-%m-%Y")
            start = start.strftime("%I:%M %p")
            end = end.strftime("%I:%M %p")
            speak(event['summary'] + f"from {start} to {end}")
            print(event_date, start," to ", end, event['summary'])

def create_events(service):
    event = {
      'summary': 'Google I/O 2015',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': '2021-08-19T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2021-08-19T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))


DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAY_EXTENSIONS = ['rd', 'th', 'st', 'nd']

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today")>0:
        return today

    day=-1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found>0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month <today.month and month!=-1:
        year=year+1
    if day< today.day and month==-1 and day!=-1:
        month = month+1
    if month==-1 and day==-1 and day_of_week !=-1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif<0:
            dif+=7
            if text.count("next")>=1:
                dif+=7
        return today + datetime.timedelta(dif)
    if month==-1 or day==-1:
        return None
    return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":","-")+"-note.txt"
    with open(file_name, 'w') as f:
        f.write(text)
    subprocess.Popen(["notepad.exe", file_name])

def get_random(res_list):
    return random.sample(res_list, 1)[0]

def joke():
    return get_jokes("en")

SERVICE = google_auth()

GREETING_STRS = ["hi", 'hey', 'whats up', 'hai', 'hello', "you there"]
INTRO_STRS = ["what should i call you", "your name", "who are you"]
END_STRS = ["bye", "goodbye"]
TIME_STRS = ["current time", "time now"]
CALENDAR_STRINGS = ["plans on", "what do i have", "do i have plans", "am i busy", "events", "what's the plan on"]
NOTE_STRS = ['make a note', 'write this down', 'remember this', "take a note"]
WHAT_STRS = ["what is", "define", "definition"]
JOKE_STRS = ["tell me a joke",]

# RESPONSE LISTS
NAME_LIST = ["You can call me Dora", "I am Dora", "I am Dora, How can I help you?"]
GREETING_LIST = ["How can I help you?", "hi", 'hey', 'whats up', 'hello']

while True:
    text = get_audio()

    if text is not None:


        if any(phrase in text for phrase in GREETING_STRS):
            speak(get_random(GREETING_LIST))

        elif any(phrase in text for phrase in INTRO_STRS):
            speak(get_random(NAME_LIST))

        elif any(phrase in text for phrase in TIME_STRS):
            current_time = datetime.datetime.now()
            current_time = current_time.strftime("%I:%M %p")
            speak("Current time is : " + str(current_time))

        elif any(phrase in text for phrase in JOKE_STRS):
            speak(get_random(get_jokes("en")))

        elif any(phrase in text for phrase in CALENDAR_STRINGS):
            date = get_date(text)
            if date:
                get_events(date, SERVICE)
            else:
                speak("I don't understand")

        elif any(phrase in text for phrase in NOTE_STRS):
            speak("What would you like me to write down?")
            note_text = get_audio()
            note(note_text)
            speak("I have made a note for that.")

        elif any(phrase in text for phrase in WHAT_STRS):
            res = pywhatkit.info(text, return_value=True)
            if res is not None:
                speak("Accourding to wikipedia " + str(res))
            else:
                speak("I don't understand")

        elif "thank" in text:
            speak("I am always happy to help you")

        elif any(phrase in text for phrase in END_STRS):
            speak("Bye!, have a nice day!")
            break       