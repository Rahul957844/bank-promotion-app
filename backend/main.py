from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# ---------------- Database Setup ----------------
DATABASE_URL = "postgresql://postgres_username_password_at_host_5432_user:HXunPUi1argogvua4FNPwbusTsOcM0nP@dpg-d2pedd56ubrc73c8sgu0-a.oregon-postgres.render.com/postgres_username_password_at_host_5432"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bank-promotion-757bne3xn-sandhya-s-projects-5016aed4.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Models ----------------
class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, index=True)
    introducer_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    beneficiary_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)

    introducer = relationship("Account", remote_side=[account_id], foreign_keys=[introducer_id])
    beneficiary = relationship("Account", remote_side=[account_id], foreign_keys=[beneficiary_id])

Base.metadata.create_all(bind=engine)

# ---------------- Schemas ----------------
class AccountCreate(BaseModel):
    account_id: int
    introducer_id: int | None = None

# ---------------- Routes ----------------
@app.get("/")
def read_root():
    return {"message": "Bank API is running!"}

@app.get("/accounts/")
def get_accounts():
    db = SessionLocal()
    try:
        accounts = db.query(Account).all()
        return [
            {"AccountID": acc.account_id, "IntroducerID": acc.introducer_id, "BeneficiaryID": acc.beneficiary_id}
            for acc in accounts
        ]
    finally:
        db.close()

@app.post("/accounts/")
def create_account(data: AccountCreate):
    db = SessionLocal()
    try:
        introducer = None
        if data.introducer_id:
            introducer = db.query(Account).filter(Account.account_id == data.introducer_id).first()
            if not introducer:
                raise HTTPException(status_code=400, detail="Introducer not found")

        # Count accounts introduced by this introducer
        introduced_accounts = db.query(Account).filter(Account.introducer_id == data.introducer_id).order_by(Account.account_id).all()
        sequence = len(introduced_accounts) + 1  # this account's position

        # Determine beneficiary
        if sequence % 2 == 1:  # odd
            beneficiary_id = data.introducer_id
        else:  # even
            if introducer.introducer_id:  # introducer has an introducer
                parent_introducer = db.query(Account).filter(Account.account_id == introducer.introducer_id).first()
                beneficiary_id = parent_introducer.beneficiary_id if parent_introducer else None
            else:
                beneficiary_id = None

        new_acc = Account(
            account_id=data.account_id,
            introducer_id=data.introducer_id,
            beneficiary_id=beneficiary_id
        )
        db.add(new_acc)
        db.commit()
        db.refresh(new_acc)

        return {
            "AccountID": new_acc.account_id,
            "IntroducerID": new_acc.introducer_id,
            "BeneficiaryID": new_acc.beneficiary_id
        }
    finally:
        db.close()
