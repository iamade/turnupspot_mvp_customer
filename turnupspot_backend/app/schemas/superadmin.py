from pydantic import BaseModel

class SuperAdminStats(BaseModel):
    total_users: int
    total_events: int
    total_vendors: int 