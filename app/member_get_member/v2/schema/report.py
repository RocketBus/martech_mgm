from sqlmodel import SQLModel

class ReportBase(SQLModel):
    purchase_approved: int = 0
    guest_registered: int = 0
    guest_boarded: int = 0
    selected_ticket: int = 0
    applied_coupon: int = 0
    completed_purchase: int = 0