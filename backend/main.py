from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# ---------------- Database Setup ----------------
# ✅ Replace this with your actual Render PostgreSQL URL
DATABASE_URL = "postgresql://postgres_username_password_at_host_5432_user:HXunPUi1argogvua4FNPwbusTsOcM0nP@dpg-d2pedd56ubrc73c8sgu0-a.oregon-postgres.render.com/postgres_username_password_at_host_5432"

print("📌 Using database URL:", DATABASE_URL)  # debug log

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bank-promotion-757bne3xn-sandhya-s-projects-5016aed4.vercel.app",  # frontend
    "http://localhost:3000",  # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
print("✅ Database tables created")  # debug log

# ---------------- Schemas ----------------
class AccountCreate(BaseModel):
    account_id: int
    introducer_id: int | None = None

# ---------------- Routes ----------------
@app.get("/")
def read_root():
    print("➡️ GET / called")  # debug log
    return {"message": "Bank API is running!"}

@app.get("/accounts/")
def get_accounts():
    print("➡️ GET /accounts/ called")  # debug log
    db = SessionLocal()
    accounts = db.query(Account).all()
    return [
        {"AccountID": acc.account_id, "IntroducerID": acc.introducer_id, "BeneficiaryID": acc.beneficiary_id}
        for acc in accounts
    ]

@app.post("/accounts/")
def create_account(data: AccountCreate):
    print("➡️ POST /accounts/ called with:", data.dict())  # debug log
    db = SessionLocal()

    introducer = None
    if data.introducer_id:
        introducer = db.query(Account).filter(Account.account_id == data.introducer_id).first()
        if not introducer:
            print("❌ Introducer not found:", data.introducer_id)  # debug log
            raise HTTPException(status_code=400, detail="Introducer not found")

    # count how many accounts this introducer has introduced
    count = db.query(Account).filter(Account.introducer_id == data.introducer_id).count() + 1
    print(f"Introducer {data.introducer_id} has introduced {count} accounts")  # debug log

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

    print("✅ Account created:", new_acc.account_id)  # debug log

    return {
        "AccountID": new_acc.account_id,
        "IntroducerID": new_acc.introducer_id,
        "BeneficiaryID": new_acc.beneficiary_id
    }
