import os
import base64
import uvicorn
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from pydantic import BaseModel

from models import LoginSchema, SignUpSchema, ChunkSchema, BaseSchema

#import pyrebase
#import config
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter
from openai import OpenAI

import pronunciationChecking
import ipaTransliteration as epi
import random
import librosa
import soundfile as sf
import numpy as np

from dotenv import load_dotenv
load_dotenv()

import requests
import traceback

if not firebase_admin._apps:
    #check if file exists
    if os.path.exists("spanish-pronunciation-pro-firebase-adminsdk-fbsvc-af37a865d2.json"):
        cred = credentials.Certificate("spanish-pronunciation-pro-firebase-adminsdk-fbsvc-af37a865d2.json")
    else:
        firebase_creds_json = os.environ.get("FIREBASE_CREDENTIALS")
        temp_path = "/tmp/firebase_credentials.json"
        with open(temp_path, "w") as f:
            f.write(firebase_creds_json)
        cred = credentials.Certificate(temp_path)
    firebase_admin.initialize_app(cred)

app = FastAPI(
    description = "API's for the Spanish Pronunciation Pro Project",
    title = "SPP API's",
    docs_url= "/"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://spanish-pronunciation-pro.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = firestore.client()
#firebase = pyrebase.initialize_app(config.firebaseConfig)

class AudioData(BaseModel):
    base64_data: str

class TranscriptionData(BaseModel):
     sentence: str
     base64_data: str
# openai import
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/sendVoiceNote")
async def send_voice_note(data: AudioData):
    try:
        # Decode base64 string
        audio_bytes = base64.b64decode(data.base64_data)

        # Write to disk
        audio_file_name = "audio.webm"
        with open(audio_file_name, "wb") as f:
            f.write(audio_bytes)

        # Transcribe using OpenAI Whisper
        with open(audio_file_name, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="es" 
            )

        return transcript  # returns raw text
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing audio: {str(e)}"
        )
      
"""
@app.post("/signup")
async def signup(request: SignUpSchema):
    email = request.email
    password = request.password
    displayName = request.displayName

    date = datetime.now()
    ret_date = date.strftime("%B") + "," + str(date.year)

    try:
        # Look into password hashing.
        # salt = bcrypt.gensalt()   

        user = auth.create_user(
            email = email,
            password = password,
        )

        doc_ref = db.collection('users').document()
        data = {
            'name': displayName,
            'id': user.uid,
            'creation_date': ret_date
        }
        doc_ref.set(data)

        return JSONResponse(content={"id": data['id']}, 
                                status_code = 201)

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code = 400,
            detail= f"Account exists with this email."
        )
"""
    
""" UNUSED
@app.post("/login")
async def login(request: LoginSchema):
    email = request.email
    password = request.password

    try:
        user = auth().sign_in_with_email_and_password(
            email = email,
            password = password
        )
        id = user['idToken']

        print(user['localId'])

        # user.localId gives id for database purposes
        return JSONResponse(
            content={
                "user_ids": {
                    "auth_id": id,
                    "local_id": user['localId']
                }
            },
            status_code=201
)
    except Exception as e:
        raise HTTPException(
            status_code = 400,
            detail= f"Incorrect login information. {str(e)}"
        )
"""

# user statistics are display on the profile page.
@app.get("/getUserStatistics")
async def getUserStatistics(uid):
    try:
        
        doc_ref = db.collection('stats')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        
        return JSONResponse(content={"user_stats": query_ref[0].to_dict()},
                             status_code=201)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error finding user statistics. {str(e)}"
        )
    
# Initialize the user statistics after the user creates an account.
@app.post("/setUserStatistics")
async def setUserStatistics(request: BaseSchema):
    try:
        doc_ref = db.collection('stats')

        data = {
            'accuracy_rate': int(0),
            'id': request.id,
            'completed_lessons': int(0),
            'practice_sessions': int(0),
            'study_streak': int(0),
            'uses': int(0)
        }

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", request.id)).get()
        if(query_ref):
                    raise HTTPException(
                    status_code=400,
                    detail= f"User statistics already exist."
                ) 
        else:
            doc = doc_ref.document()
            doc.set(data)
            return JSONResponse(content={"message": "User statistics were successfully intialized."}, 
                                    status_code = 201)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error intializing user statistics {str(e)}."
        )

# After calculating the users new accuracy, update the accuracy value.
@app.patch("/updateAccuracy")
async def updateAccuracy(uid, new_accuracy):
    try:
        doc_ref = db.collection('stats')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('stats').document(doc_id).update({"accuracy_rate": new_accuracy})
        return JSONResponse(content={"message": f"Accuracy was successfully updated to a value of {int(new_accuracy)}%" }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error updating user accuracy. {str(e)}"
        )
    
# When the user completes a practice session, update the value.
@app.patch("/updatePracticeSessions")
async def updatePracticeSessions(uid):
    try:
        doc_ref = db.collection('stats')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('stats').document(doc_id).update({"practice_sessions": firestore.Increment(1)})
        return JSONResponse(content={"message": f"User has successfully completed a practice session." }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error completing practice session. {str(e)}"
        )

# When the user finishes all the chunks present in a lesson, update the amount of lessons they've completed.
@app.patch("/updateCompletedLessons")
async def updateCompletedLessons(uid):
    try:
        doc_ref = db.collection('stats')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('stats').document(doc_id).update({"completed_lessons": firestore.Increment(1)})
        return JSONResponse(content={"message": f"User has successfully completed a lesson, the amount of lessons they've completed has been incremented." }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error completing lesson. {str(e)}"
        )
    
# When a user logs in consecutively update their study streak.
@app.patch("/updateStudyStreak")
async def updateStudyStreak(uid):
    try:
        doc_ref = db.collection('stats')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('stats').document(doc_id).update({"study_streak": firestore.Increment(1)})
        return JSONResponse(content={"message": f"User has logged in consecutively, study streak was incremented." }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error updating streak. {str(e)}"
        )
   
# When a user uses the pronounciation checker, update the value.
@app.patch("/updateUses")
async def updateUses(uid):
    try:
        doc_ref = db.collection('stats')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('stats').document(doc_id).update({"uses": firestore.Increment(1)})
        return JSONResponse(content={"message": f"User has used the pronounciation checker, pronounciation uses has been incremented." }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error updating pronounciation uses. {str(e)}"
        )
   
# Get the lessons that the user has previously completed.
@app.get("/getLessonProgress")
async def getLessonProgress(uid):
    try:
        doc_ref = db.collection('lessons')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()

        data = query_ref[0].to_dict()

        print(data)

        return JSONResponse(content={"lessons": data},
                            status_code=201)
    except Exception as e:
                raise HTTPException(
            status_code=400,
            detail= f"Error loading lesson data. {str(e)}"
        )

# Initializes the achievement array.
@app.post("/setAchievements")
async def setAchievements(request: BaseSchema):
     try:
          doc_ref = db.collection('achievements')

          query_ref = doc_ref.where(filter=FieldFilter("id", "==", request.id)).get()
          if(query_ref):
                    raise HTTPException(
                    status_code=400,
                    detail= f"Achievements already exist"
                )
          else: 
            doc = doc_ref.document()
            data = {
                 'id': request.id,
                 'achievements': []
            }
            doc.set(data)

            return JSONResponse(content={"message": "Achievments were successfully initialized."}, 
                                    status_code = 201)
     except Exception as e:
                         raise HTTPException(
            status_code=400,
            detail= f"Error updating achievements. {str(e)}"
        )


# Set an achievment to true.
@app.patch("/updateAchievements")
async def updateAchievements(uid, achievement: int):
     try:
          doc_ref = db.collection('achievements')

          query_ref = doc_ref.where(filter=FieldFilter("id", "==", uid)).get()
          
          doc = query_ref[0]
          doc_id = doc.id
          achievements = doc.to_dict().get('achievements', [])

          if (achievement >= len(achievements) and achievement < 30):
               new_size = achievement - len(achievements) + 1
               achievements.extend([False] * new_size)

          achievements[achievement] = True
          
          doc_ref = db.collection('achievements').document(doc_id).update({"achievements": achievements})

          return JSONResponse(content={"message": f"User has successfully earned achievement {achievement}"},
                            status_code=201)      
        
     except Exception as e:
                         raise HTTPException(
            status_code=400,
            detail= f"Error updating achievements. {str(e)}"
        )


# Get the user achievments from the database.
@app.get("/getAchievements")
async def getAchievements(uid):
    try:
        doc_ref = db.collection('achievements')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()

        return JSONResponse(content={"achievements": query_ref[0].to_dict()},
                            status_code=201)
    except Exception as e:
                         raise HTTPException(
            status_code=400,
            detail= f"Error fetching user achievements. {str(e)}"
        )

# Push newest activity to the activities array, if the list is full then pop the old activities.
@app.patch("/updateActivityHistory")
async def updateActivityHistory(uid, activity):
    try:
        doc_ref = db.collection('activity_history')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        if (not query_ref):
            new_doc = doc_ref.document()
            new_doc.set({'activities': [activity], 'id': uid})
        else:
            doc_id = query_ref[0].id
            doc_ref = db.collection('activity_history').document(doc_id).get()
            activities = doc_ref.to_dict().get('activities', [])

            while(len(activities) >= 3 and len(activities) > 0):
                activities.pop(0)

            activities.append(activity)

            doc_ref = db.collection('activity_history').document(doc_id).update({"activities": activities})
        return JSONResponse(content={"message": f"User's recent activity has been added to their history.'" }, 
                                    status_code = 201)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error updating activity history. {str(e)}"
        )

# Get the activities array from the database
@app.get("/getActivityHistory")
async def getActivityHistory(uid):
    try: 
        doc_ref = db.collection('activity_history')
        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        doc_id = query_ref[0].id
        doc_ref = db.collection('activity_history').document(doc_id).get()
        activities = doc_ref.to_dict().get('activities', [])

        return JSONResponse(content={"activity_history": activities }, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error fetching activity history. {str(e)}"
        )

@app.post("/setUser")
async def setUser(request: BaseSchema):
    try:
            doc_ref = db.collection('users')

            query_ref = doc_ref.where(filter= FieldFilter("id", "==", request.id)).get()

            if(query_ref):
                    raise HTTPException(
                    status_code=400,
                    detail= f"User already exists"
                )
            else: 
                doc = doc_ref.document()
                data = {
                    'id': request.id,
                    'initialized': True
                }
            doc.set(data)

            return JSONResponse(content={"user": data}, 
                                status_code=201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error fetching user, No user exists. {str(e)}"
        )

@app.get("/getUser")
async def getUser(uid):
    try:
            doc_ref = db.collection('users')

            query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
            stats = query_ref[0].to_dict()

            return JSONResponse(content={"user": stats}, 
                                status_code=201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error fetching user, No user exists. {str(e)}"
        )

# Fetch the user accuracy
@app.get("/getUserAccuracy")
async def getUserAccuracy(uid):
    try: 
        doc_ref = db.collection('stats')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
        stats = query_ref[0].to_dict()
        
        return JSONResponse(content={"accuracy_rate": int(stats["accuracy_rate"])},
                            status_code=201)
    except Exception as e:
                         raise HTTPException(
            status_code=400,
            detail= f"Error fetching accuracy. {str(e)}"
        )

# Fetch the chunk progress
@app.get("/getChunkProgress")
async def getChunkProgress(uid, lesson: int):
    try:
        doc_ref = db.collection('lessons')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()

        data = query_ref[0].to_dict()

        return JSONResponse(content={"chunk_progress": data["chunks"][lesson]},
                            status_code=201)
    except Exception as e:
                raise HTTPException(
            status_code=400,
            detail= f"Error getting chunk progress. {str(e)}"
        )

# Set a chunk to completed, (Stored as a map as firestore does not allow the storage of 2-d arrays / lists)
@app.patch("/updateChunkProgress")
async def updateChunkProgress(uid, chunk: str, lesson: int, difficulty: str):
    try:
        doc_ref = db.collection('lessons')

        query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()

        doc = query_ref[0]
        doc_id = doc.id
        data = doc.to_dict()
        chunks = data.get('chunks', [])

        if chunks[lesson] is None:
              chunks[lesson] = {}

        chunks[lesson][chunk+"-"+difficulty] = True
        print(chunks)

        doc_ref = db.collection('lessons').document(doc_id).update({"chunks": chunks})

        return JSONResponse(content={"message": "Chunk was successfully updated."},
                            status_code=201)
    except Exception as e:
                raise HTTPException(
            status_code=400,
            detail= f"Error updating chunk progress. {str(e)}"
        )

# Updates the lesson progress array in the lessons collection.
@app.patch("/updateLessonProgress")
async def updateLessonProgress(uid, lesson: int):
     try:
          doc_ref = db.collection('lessons')
          query_ref = doc_ref.where(filter= FieldFilter("id", "==", uid)).get()
          doc_id = query_ref[0].id
          data = query_ref[0].to_dict()
          data['lesson_data'][lesson]['completed'] = True
          print(data['lesson_data'])

          doc_ref = db.collection('lessons').document(doc_id).update({"lesson_data": data['lesson_data']})

          return JSONResponse(content={"message": "Lesson progress was successfully updated."}, 
                                    status_code = 201)
        
     except Exception as e:
         raise HTTPException(
              status_code=400,
              detail= f"Error updating lesson progress. {str(e)}"
         )

# Sets the lesson progress to false and initializes the chunk array.
@app.post("/setLessonProgress")
async def setLessonProgress(request: BaseSchema):
    try:
         doc_ref = db.collection('lessons')

         query_ref = doc_ref.where(filter= FieldFilter("id", "==", request.id)).get()
         if(query_ref):
                    raise HTTPException(
                    status_code=400,
                    detail= f"Lesson Progress already exists"
                ) 
         else:
            doc = doc_ref.document()
            data = {
              'id': request.id,
              'lesson_data': [
                   {'completed': False, 'completion_date': None} for _ in range(7)
              ],
              'chunks': [None] * 7
            }

            doc.set(data)

            return JSONResponse(content={"message": "Lesson progress was successfully intialized."}, 
                                    status_code = 201)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail= f"Error intializing lesson progress {str(e)}."
        )
    
@app.post("/generateSentence")
async def generateSentence(chunk: str, lesson: str, difficulty: str):
      client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
      try:
        prompt = (
            f"You are a helpful assistant that generates Spanish sentences or words for a pronunciation app. "
            f"The current lesson chunk is '{chunk}', the specific lesson is '{lesson}', and the difficulty is '{difficulty}'. "
            f"Generate ONLY the Spanish sentence or word requested, with NO extra text, explanations, or introductions. Do not say anything like 'Here is a sentence:' or 'OK'. Just output the Spanish sentence or word itself. "
            f"Use the Spanish alphabet and correct accent marks. "
            f"If the difficulty is or includes 'word', return only a single word."
        )
        user_content = (
            f"Generate a Spanish {difficulty} for the lesson '{lesson}' in the chunk '{chunk}'. "
            f"ONLY return the Spanish sentence or word, and nothing else."
        )
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": prompt},
                        {"role": "user", "content": user_content}],
                temperature=1
        )
        current_sentence = response.choices[0].message.content
      # if there is an error with OpenAI, use a backup list of sentences
      except:
            backup_sentences = [
                "El gato duerme.", "La niña corre.", 
                "El perro ladra.", "Hace mucho calor.",
                "Llueve afuera.", "El vaso está lleno.",
                "La casa es grande.", "El pan está caliente.",
                "Hay una flor.", "La cama es cómoda."
            ]
            current_sentence = random.choice(backup_sentences)
      finally:
        return current_sentence

@app.post("/checkPronunciation")
async def checkPronunciation(data: TranscriptionData):
      try:
        
        audio_bytes = base64.b64decode(data.base64_data)
        sentence = data.sentence

        with open("audio.wav", "wb") as f:
              f.write(audio_bytes)
        
        print(os.path.isfile('audio.wav'))
        audio, sampling_rate = librosa.load('audio.wav', sr=16000, mono=True, duration=30.0, dtype=np.int32)
        sf.write('tmp.wav', audio, 16000)
        output = pronunciationChecking.correct_pronunciation(sentence, "tmp.wav", 'latam')

        # Get rid of audio recordings
        if os.path.exists("audio.wav"):
            os.remove("audio.wav")
            print(f"File deleted successfully.")
        else: print(f"File not found.")
        if os.path.exists("tmp.wav"):
            os.remove("tmp.wav")
            print(f"File deleted successfully.")
        else: print(f"File not found.")
      except Exception as e:
            print('Error: ', str(e))
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error in pronunciation checking: {str(e)}"
            )

      return output

@app.post("/translate")
async def translate(request: Request):
    body = await request.json()
    response = requests.post("https://libretranslate.de/translate", json=body)
    return response.json()
