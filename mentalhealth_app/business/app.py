from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic
from sqlalchemy.orm import Session
from datetime import datetime
import matplotlib.pyplot as plt
import io
import re
import base64
from typing import Optional, List
# Correct imports from your modules
from mentalhealth_app.data.database import engine, get_db, Base  # Add Base here
from .services.icd_service import ICDService
from .models import ActivityEntry, JournalEntry, User, MoodEntry

# Create tables - NOW WITH ACCESS TO Base
Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBasic()

# Password hashing (in production use bcrypt)
def get_password_hash(password: str):
    # In production, use: bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return f"hashed_{password}"  # Simple hash for development


# Authentication
async def authenticate_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.hashed_password != get_password_hash(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.get("/icd/categories")
async def get_mental_health_categories(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Fix: Add await here
    user = await authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
        icd_service = ICDService()
        return await icd_service.get_mental_health_categories()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/icd/search")
async def search_icd_conditions(
    query: str = Form(..., min_length=2),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Authenticate
        user = await authenticate_user(username, password, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Perform search
        icd_service = ICDService()
        raw_results = await icd_service.search_conditions(query)
        
        # Format results consistently
        results = []
        for item in raw_results:
            results.append({
                "code": item.get("theCode", ""),
                "title": item.get("title", ""),
                "definition": item.get("definition", ""),
                "entity_id": item.get("id", ""),
                # Remove HTML tags from title
                "clean_title": re.sub(r'<[^>]+>', '', item.get("title", ""))
            })
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

# Endpoints
@app.post("/mood_history")
async def mood_history(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    entries = db.query(MoodEntry).filter(MoodEntry.user_id == user.id).order_by(MoodEntry.created_at.desc()).limit(10).all()
    return [
        {
            "score": entry.score,
            "notes": entry.notes,
            "created_at": entry.created_at.isoformat()
        }
        for entry in entries
    ]

@app.post("/activity_history")
async def activity_history(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Strictly filter by user_id and verify ownership
    entries = db.query(ActivityEntry).filter(
        ActivityEntry.user_id == user.id
    ).order_by(
        ActivityEntry.created_at.desc()
    ).limit(20).all()
    
    if not entries:
        return []
        
    return [
        {
            "activity": entry.activity,
            "duration": entry.duration,
            "created_at": entry.created_at.isoformat()
        }
        for entry in entries
    ]

@app.post("/journal_history")
async def journal_history(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(username, password, db)  # Add await here
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == user.id  # Now works correctly
    ).order_by(
        JournalEntry.created_at.desc()
    ).limit(20).all()
    
    return [
        {
            "entry": entry.entry,
            "created_at": entry.created_at.isoformat()
        }
        for entry in entries
    ]

@app.get("/")
async def root():
    return {
        "message": "Mental Health Tracker API",
        "endpoints": {
            "register": "POST /register",
            "log_mood": "POST /mood",
            "get_insights": "GET /insights/{username}",
            "mood_chart": "GET /mood_chart/{username}"
        }
    }

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Check for existing username
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Check for existing email if provided
    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )
    
    # Create new user
    db_user = User(
        username=username,
        hashed_password=get_password_hash(password),
        email=email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"status": "success", "user_id": db_user.id}

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    # In production, use: bcrypt.checkpw(password.encode(), user.hashed_password.encode())
    if user.hashed_password != get_password_hash(password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username
    }

@app.post("/mood")
async def log_mood(
    username: str = Form(...),
    password: str = Form(...),
    score: int = Form(..., ge=1, le=10),  # Score between 1-10
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create mood entry
    mood_entry = MoodEntry(
        user_id=user.id,
        score=score,
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(mood_entry)
    db.commit()
    
    return {
        "status": "success",
        "message": "Mood logged successfully",
        "score": score,
        "timestamp": mood_entry.created_at.isoformat()
    }

@app.post("/activity")
async def log_activity(
    username: str = Form(...),
    password: str = Form(...),
    activity: str = Form(...),
    duration: int = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    entry = ActivityEntry(
        user_id=user.id,
        activity=activity,
        duration=duration,
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    return {"status": "success"}


@app.post("/journal")
async def log_journal(
    username: str = Form(...),
    password: str = Form(...),
    entry: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await authenticate_user(username, password, db)  # Add await here
    journal = JournalEntry(
        user_id=user.id,  # Now works correctly
        entry=entry,
        created_at=datetime.utcnow()
    )
    db.add(journal)
    db.commit()
    return {"status": "success"}

@app.get("/insights/{username}")
async def get_insights(
    username: str,
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Authenticate
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get user's mood entries
    entries = db.query(MoodEntry).filter(MoodEntry.user_id == user.id).all()
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No mood entries found"
        )
    
    scores = [entry.score for entry in entries]
    
    return {
        "username": username,
        "entry_count": len(entries),
        "average_mood": sum(scores)/len(scores),
        "last_7_days": [e.score for e in entries[-7:]]
    }

@app.get("/mood_chart/{username}")
async def mood_chart(
    username: str,
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Authenticate
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get user's mood entries
    entries = db.query(MoodEntry).filter(MoodEntry.user_id == user.id).order_by(MoodEntry.created_at).all()
    
    if len(entries) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 2 entries to generate chart"
        )
    
    # Prepare chart data
    dates = [entry.created_at for entry in entries]
    scores = [entry.score for entry in entries]
    
    # Generate plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, scores, 'b-o')
    plt.title(f"Mood Trend for {username}")
    plt.xlabel("Date")
    plt.ylabel("Mood Score (1-10)")
    plt.ylim(0, 11)
    plt.grid(True)
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()
    
    return JSONResponse({
        "chart": base64.b64encode(buf.read()).decode('utf-8'),
        "username": username
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)