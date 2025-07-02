# shared/models.py
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
# from sqlalchemy.orm import relationship
from .databases import Base

class User(Base):
    """Table pour l'authentification globale"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Wallet(Base):
    """Table pour les wallets indépendants"""
    __tablename__ = "wallets"
    
    address = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    wallet_password_hash = Column(String) 
    currency = Column(String)
    balance = Column(Float, default=0.0)
    is_locked = Column(Boolean, default=False)
    
class Transaction(Base):
    """Table pour les transactions"""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True)
    wallet_address = Column(String, ForeignKey("wallets.address"), nullable=False)
    amount = Column(Float, nullable=False)
    external_wallet = Column(String)
    transaction_type = Column(String)
    description = Column(String, nullable=True)
    status = Column(String)  # "pending", "completed", "failed"
    retry_count = Column(String , default=0)
 
        