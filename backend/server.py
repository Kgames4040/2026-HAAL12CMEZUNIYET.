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
    friends_data = [
        {"id": i, "name": f"Friend {i}", "photos": [
            f"https://picsum.photos/seed/{i}-1/400/600",
            f"https://picsum.photos/seed/{i}-2/400/600",
            f"https://picsum.photos/seed/{i}-3/400/600"
        ]} for i in range(1, 21)
    ]
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

class Friend(BaseModel):
    id: int
    name: str
    photos: List[str]

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