import platform
import asyncio

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from threading import Thread

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List
import uuid
from pymongo import MongoClient
import os
import smtplib
from email.mime.text import MIMEText
import pickle
import tensorflow as tf
import numpy as np
from email_sender import send_complaint_email
import cloudinary
import cloudinary.uploader
import os

model = tf.keras.models.load_model("fixit_model.keras")

CLASS_NAMES = [
    "garbage",
    "potholes",
    "stray_animals",
    "street_lights"
]

DEPARTMENTS = {
    "garbage": "Municipal Corporation",
    "potholes": "Municipal Corporation",
    "stray_animals": "Municipal Corporation",
    "street_lights": "Electricity Department"
}
def predict_issue(image_path):
    img = tf.keras.utils.load_img(image_path, target_size=(224,224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, 0)

    prediction = model.predict(img_array)

    idx = np.argmax(prediction)

    return {
        "issue": CLASS_NAMES[idx],
        "department": DEPARTMENTS[CLASS_NAMES[idx]]
    }
app = FastAPI()
cloudinary.config(
    cloud_name=os.getenv("dlxcp4fyf"),
    api_key=os.getenv("192131941273286"),
    api_secret=os.getenv("3MR-D1VZq8Y_aV-CXTDcKzWwi7Q"),
    secure=True
)
MONGO_URI = "mongodb+srv://aryan:aryan5643@fixit.f1dekoj.mongodb.net/?appName=Fixit"

client = MongoClient(MONGO_URI)

db = client["civic_feed"]

complaints_collection = db["complaints"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fixit-9f13.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



complaints = []

class Complaint(BaseModel):
    id: str
    issue_type: str
    description: str
    location: str
    image: str | None = None
    authority: str

def predict_issue(image_path):

    img = tf.keras.utils.load_img(
        image_path,
        target_size=(224,224)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, 0)

    prediction = model.predict(img_array)
    print("Raw Prediction:", prediction)
    print("Predicted Index:", np.argmax(prediction))
    idx = np.argmax(prediction)
    issue = CLASS_NAMES[idx]

    mapping = {
        "garbage": "Municipal Corporation",
        "potholes": "Municipal Corporation",
        "stray_animals": "Municipal Corporation",
        "street_lights": "Electricity Department"
    }
    print(CLASS_NAMES)
    print("Index:", idx)
    print("Resolved Class:", CLASS_NAMES[idx])

    return {
        "issue": issue,
        "department": mapping[issue]
    }

DEPARTMENT_EMAILS = {
    "Municipal Corporation": "sinha.anjali069@gmail.com",
    "Water Department": "waterdept@example.com",
    "Electricity Department": "electricity@example.com",
    "Police Department": "police@example.com",
    "General Civic Department": "general@example.com"
}

def send_department_email(complaint):

    recipient = DEPARTMENT_EMAILS.get(
        complaint["authority"]
    )

    if not recipient:
        return

    subject = (
        f"[FixIt] {complaint['issue_type']} "
        f"reported at {complaint['location']}"
    )

    body = f"""
Dear {complaint['authority']},

A new civic complaint has been assigned.

Issue Type:
{complaint['issue_type']}

AI Classification:
{complaint['ai_prediction']}

Location:
{complaint['location']}

Description:
{complaint['description']}

Reported By:
{complaint['user_name']}
{complaint['user_email']}

Please review and take necessary action.

Regards,
FixIt Platform
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "sinha.aryan5643@gmail.com"
    msg["To"] = recipient

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        "sinha.aryan5643@gmail.com",
        "lqwf qahe etdx zfly"
    )

    server.send_message(msg)
    server.quit()
@app.get("/")
def home():
    return {"message": "Civic Problem API Running"}

from fastapi.encoders import jsonable_encoder

@app.get("/complaints")
def get_complaints():

    complaints = list(
        complaints_collection.find()
    )

    for complaint in complaints:

        complaint["_id"] = str(
            complaint["_id"]
        )

    return jsonable_encoder(
        complaints
    )


@app.post("/like/{complaint_id}")
def like_complaint(complaint_id: str):

    complaints_collection.update_one(
        {"id": complaint_id},
        {"$inc": {"likes": 1}}
    )

    complaint = complaints_collection.find_one(
        {"id": complaint_id}
    )

    return {
        "likes": complaint["likes"]
    }
class CommentRequest(BaseModel):
    user: str
    text: str
@app.post("/comment/{complaint_id}")
def add_comment(
    complaint_id: str,
    comment: CommentRequest
):

    complaints_collection.update_one(
        {"id": complaint_id},
        {
            "$push": {
                "comments": {
                    "user": comment.user,
                    "text": comment.text
                }
            }
        }
    )

    return {
        "message": "Comment added"
    }

@app.post("/report")
async def report_issue(
    issue_type: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    city: str = Form(...),

    user_name: str = Form(...),
    user_photo: str = Form(...),
    user_email: str = Form(...),

    image: UploadFile | None = File(None)
):
    
    image_url = None
    image_path = None
    import tempfile
    if image:
        file_bytes = await image.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(file_bytes)
            image_path = tmp.name

        upload_result = cloudinary.uploader.upload(
            file_bytes,
            folder="fixit"
        )

        image_url = upload_result["secure_url"]

    if image_path:
        result = predict_issue(image_path)
    else:
        result = {
            "issue": issue_type,
            "department": "Municipal Corporation"
        }

    authority = result["department"]
    predicted_issue = result["issue"]
    AUTHORITY_EMAILS = {
        "gurgaon": {
        "Municipal Corporation": "support@mcg.gov.in",
        "Electricity Department": "1912@dhbvn.org.in",
        "Police": "cp.ggn@hry.nic.in"
        },

        "delhi": {
        "Municipal Corporation": "mcd-ithelpdesk@mcd.nic.in",
        "Electricity Department": "pspower@nic.in",
        "Police": "cpdelhi@delhipolice.gov.in"
     },

        "mumbai": {
        "Municipal Corporation": "mcgm@mcgm.gov.in",
        "Electricity Department": "helpdesk.mumbaielectricity@adani.com",
        "Police": "cp.mumbai@mahapolice.gov.in"
        },

        "chennai": {
        "Municipal Corporation": "commissioner@chennaicorporation.gov.in",
        "Electricity Department": "cpro@tnebnet.org",
        "Police": "cop.chncity@tncctns.gov.in"
        }
    }

    receiver_email = AUTHORITY_EMAILS[city.lower()][authority]
    print("AI Issue:", predicted_issue)
    print("AI Authority:", authority)
    complaint = {

    "id": str(uuid.uuid4()),

    "user_name": user_name,

    "user_photo": user_photo,

    "user_email": user_email,

    "issue_type": issue_type,

    "description": description,

    "location": location,

    "image": image_url,

    "authority": authority,
    "ai_prediction": predicted_issue,

    "likes": 0,
    "comments": [],
    }


    result = complaints_collection.insert_one(
        complaint
    )
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    complaint["_id"] = str(
        result.inserted_id
    )

    subject = f"FixIt Complaint - {predicted_issue}"

    body = f"""
    Issue Type: {predicted_issue}

    Location:
    {location}

    Description:
    {description}

    Submitted by:
    {user_name}

    Email:
    {user_email}
    """

    #send_complaint_email(
        #receiver_email=receiver_email,
        #subject=subject,
        #body=body,
        #image_path=image_path
    #)   
