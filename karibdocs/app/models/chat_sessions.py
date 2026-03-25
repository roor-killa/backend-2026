
# / Permet de creer la structure de la table chat_sessions et chat_messages /

# app/models/chat_session.py
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    title      = Column(String(255), default="Nouvelle conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role       = Column(String(20))    # "user" ou "assistant"
    content    = Column(Text)
    sources    = Column(Text)          # JSON : sources citées
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")