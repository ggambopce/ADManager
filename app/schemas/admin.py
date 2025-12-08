from pydantic import BaseModel
from datetime import datetime

class AdminLoginRequest(BaseModel):
    loginId: str
    password: str

class AdminMeResponse(BaseModel):
    loginId: str
    createdAt: datetime
