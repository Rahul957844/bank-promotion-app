from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres_username_password_at_host_5432_user:HXunPUi1argogvua4FNPwbusTsOcM0nP@dpg-d2pedd56ubrc73c8sgu0-a.oregon-postgres.render.com/postgres_username_password_at_host_5432"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()


origins = [
    "https://bank-promotion-757bne3xn-sandhya-s-projects-5016aed4.vercel.app",  # your Vercel frontend
    "http://localhost:3000",  # for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Models ---
class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, index=True)
    introducer_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)
    beneficiary_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=True)

    introducer = relationship("Account", remote_side=[account_id], foreign_keys=[introducer_id])
    beneficiary = relationship("Account", remote_side=[account_id], foreign_keys=[beneficiary_id])

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class AccountCreate(BaseModel):
    account_id: int
    introducer_id: int | None = None

# --- API Routes ---
@app.post("/accounts/")
def create_account(data: AccountCreate):
    db = SessionLocal()
    introducer = db.query(Account).filter(Account.account_id == data.introducer_id).first()
    if data.introducer_id and not introducer:
        raise HTTPException(status_code=400, detail="Introducer not found")

    # count how many people this introducer introduced
    count = db.query(Account).filter(Account.introducer_id == data.introducer_id).count() + 1

    if count % 2 == 1:
        beneficiary_id = data.introducer_id
    else:
        beneficiary_id = introducer.introducer_id if introducer else None

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
