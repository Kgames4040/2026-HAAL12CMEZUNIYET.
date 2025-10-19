from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JSON file paths
FRIENDS_FILE = ROOT_DIR / 'data' / 'friends.json'
CODES_FILE = ROOT_DIR / 'data' / 'codes.json'
COMMENTS_FILE = ROOT_DIR / 'data' / 'comments.json'

# Ensure data directory exists
(ROOT_DIR / 'data').mkdir(exist_ok=True)

# Initialize JSON files if they don't exist
if not FRIENDS_FILE.exists():
    descriptions = [
        "The most amazing friend who always knows how to make everyone laugh. Best memories from our road trips together!",
        "My study partner through thick and thin. Couldn't have survived finals without you. Here's to many more late-night study sessions!",
        "Class clown and party starter! 🎉 You made every boring day fun. Never change your amazing energy!",
        "The most talented artist I know. Your creativity inspires everyone around you. Can't wait to see where life takes you!",
        "Future CEO in the making! Your determination and leadership skills are unmatched. Sky's the limit for you!",
        "Sports champion and team player! Your dedication on the field taught us all what true commitment means.",
        "Music genius! Every time you played, we all stopped to listen. Keep following your passion!",
        "The kindest soul with the biggest heart. You were always there when anyone needed help. Thank you for being you!",
        "Tech wizard who saved all our computers! Your coding skills are incredible. See you at Silicon Valley!",
        "Drama star! Your performances were absolutely breathtaking. Broadway is calling your name!",
        "Fashionista with impeccable style! You showed us how to express ourselves through fashion. Stay fabulous!",
        "Book lover and intellectual! Our deep conversations about life and literature will stay with me forever.",
        "Adventure seeker! From hiking trips to spontaneous road trips, you taught us to live life to the fullest!",
        "The photographer who captured all our best moments. Your eye for beauty is truly special.",
        "Future scientist! Your curiosity and analytical mind will change the world. We believe in you!",
        "The chef who made every potluck amazing! Your culinary skills are restaurant-worthy. Bon appétit!",
        "Gaming champion! Thanks for all the epic gaming sessions and teaching us strategy and teamwork.",
        "Environmental warrior! Your passion for saving the planet inspired us all to do better. Keep fighting!",
        "The poet with a way with words. Your beautiful writing touched our hearts. Never stop creating!",
        "Ultimate friend who brought us all together. You created a family out of strangers. Forever grateful! ❤️"
    ]
    
    # Sample videos that actually work
    video_urls = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    ]
    
    friends_data = []
    for i in range(1, 21):
        media = [
            {"type": "image", "url": f"https://picsum.photos/seed/student{i}-1/800/1200"},
            {"type": "image", "url": f"https://picsum.photos/seed/student{i}-2/800/1200"},
        ]
        # Add a video for every 3rd friend with variety
        if i % 3 == 0:
            video_index = (i // 3 - 1) % len(video_urls)
            media.append({"type": "video", "url": video_urls[video_index]})
        else:
            media.append({"type": "image", "url": f"https://picsum.photos/seed/student{i}-3/800/1200"})
        
        # Some friends get an extra image
        if i % 5 == 0:
            media.append({"type": "image", "url": f"https://picsum.photos/seed/student{i}-4/800/1200"})
        
        friends_data.append({
            "id": i,
            "name": f"Alex Johnson" if i == 1 else f"Student {i}",
            "quote": descriptions[i-1],
            "media": media
        })
    
    FRIENDS_FILE.write_text(json.dumps(friends_data, indent=2))

if not CODES_FILE.exists():
    codes_data = {
        f"CODE{i:03d}": f"Student {i}" for i in range(1, 21)
    }
    CODES_FILE.write_text(json.dumps(codes_data, indent=2))

if not COMMENTS_FILE.exists():
    COMMENTS_FILE.write_text(json.dumps([], indent=2))

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class LoginRequest(BaseModel):
    code: str

class LoginResponse(BaseModel):
    success: bool
    username: Optional[str] = None
    message: str

class Media(BaseModel):
    type: str  # "image" or "video"
    url: str

class Friend(BaseModel):
    id: int
    name: str
    quote: str
    media: List[Media]

class CommentCreate(BaseModel):
    friend_id: int
    username: str
    comment: str

class Comment(BaseModel):
    friend_id: int
    username: str
    comment: str
    date: str

# Helper functions
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@api_router.get("/")
async def root():
    return {"message": "Yearbook Memory API"}

@api_router.get("/friends", response_model=List[Friend])
async def get_friends():
    friends = load_json(FRIENDS_FILE)
    return friends

@api_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    codes = load_json(CODES_FILE)
    if request.code in codes:
        return LoginResponse(
            success=True,
            username=codes[request.code],
            message="Login successful"
        )
    return LoginResponse(
        success=False,
        message="Invalid code"
    )

@api_router.get("/comments/{friend_id}", response_model=List[Comment])
async def get_comments(friend_id: int):
    comments = load_json(COMMENTS_FILE)
    friend_comments = [c for c in comments if c['friend_id'] == friend_id]
    return friend_comments

@api_router.post("/comments", response_model=Comment)
async def add_comment(comment_data: CommentCreate):
    comments = load_json(COMMENTS_FILE)
    
    new_comment = {
        "friend_id": comment_data.friend_id,
        "username": comment_data.username,
        "comment": comment_data.comment,
        "date": datetime.now(timezone.utc).isoformat()
    }
    
    comments.append(new_comment)
    save_json(COMMENTS_FILE, comments)
    
    return Comment(**new_comment)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)