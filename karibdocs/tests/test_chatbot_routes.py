from app.database import SessionLocal
from app.models.chat_session import ChatMessage, ChatSession


def _register_and_login(client, email: str):
    payload = {
        "nom": "Chat User",
        "email": email,
        "telephone": "+596123456783",
        "mot_de_passe": "password123",
    }
    register = client.post("/auth/register", json=payload)
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    body = login.json()
    return body["utilisateur"]["id"], {"Authorization": f"Bearer {body['access_token']}"}


def test_chat_ask_returns_mocked_response(client, monkeypatch):
    from app.services import chat_service as chat_service_module

    user_id, headers = _register_and_login(client, "chat-ask@example.com")

    def fake_ask(self, user_id: int, question: str, session_id: int = None):
        return {
            "session_id": session_id or 999,
            "answer": f"Echo: {question}",
            "sources": ["demo.txt"],
            "chunks_used": 1,
        }

    monkeypatch.setattr(chat_service_module.ChatService, "ask", fake_ask)

    response = client.post(
        "/chat/ask",
        headers=headers,
        json={"question": "Bonjour", "session_id": None},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Echo: Bonjour"
    assert payload["sources"] == ["demo.txt"]
    assert payload["chunks_used"] == 1


def test_chat_ask_maps_runtime_error_to_503(client, monkeypatch):
    from app.services import chat_service as chat_service_module

    _user_id, headers = _register_and_login(client, "chat-runtime@example.com")

    def fake_ask_error(self, user_id: int, question: str, session_id: int = None):
        raise RuntimeError("LLM indisponible")

    monkeypatch.setattr(chat_service_module.ChatService, "ask", fake_ask_error)

    response = client.post(
        "/chat/ask",
        headers=headers,
        json={"question": "Salut", "session_id": None},
    )

    assert response.status_code == 503
    assert "LLM indisponible" in response.json()["detail"]


def test_chat_sessions_and_messages_are_user_scoped(client):
    user1_id, user1_headers = _register_and_login(client, "chat-scope-1@example.com")
    user2_id, user2_headers = _register_and_login(client, "chat-scope-2@example.com")

    db = SessionLocal()
    try:
        session1 = ChatSession(user_id=user1_id, title="Session User 1")
        session2 = ChatSession(user_id=user2_id, title="Session User 2")
        db.add(session1)
        db.add(session2)
        db.commit()
        db.refresh(session1)
        db.refresh(session2)

        db.add(ChatMessage(session_id=session1.id, role="user", content="Q1", sources="[]"))
        db.add(ChatMessage(session_id=session1.id, role="assistant", content="R1", sources='["a.txt"]'))
        db.commit()
        session1_id = session1.id
        session2_id = session2.id
    finally:
        db.close()

    sessions_response = client.get("/chat/sessions", headers=user1_headers)
    assert sessions_response.status_code == 200
    sessions_payload = sessions_response.json()
    assert any(entry["id"] == session1_id for entry in sessions_payload)
    assert all(entry["id"] != session2_id for entry in sessions_payload)

    messages_response = client.get(f"/chat/sessions/{session1_id}/messages", headers=user1_headers)
    assert messages_response.status_code == 200
    messages_payload = messages_response.json()
    assert len(messages_payload) == 2

    forbidden_response = client.get(f"/chat/sessions/{session1_id}/messages", headers=user2_headers)
    assert forbidden_response.status_code == 404
