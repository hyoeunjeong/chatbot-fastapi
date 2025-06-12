

---

# 🌠 운세 GPT 챗봇 프로젝트

“오늘의 운세 알려줄까요?”
이름 · 생년월일 · 성별 · 고민을 입력하면 AI가 분석하여 **맞춤 운세**를 제공하고, **기록까지 저장해주는 감성 운세 챗봇**입니다. 🍀

---
# 🐼개발이유 

평소에 운세 보는 걸 좋아해서, 하루 시작 전에 재미 삼아 별자리나 오늘의 띠별 운세 같은 걸 자주 보았습니다
그러다 우연히 ChatGPT를 무료로 사용해보다가, 단순한 키워드 분석이 아니라 말투나 감정까지 파악해서 답변해주는 걸 보고 신기했습니다
그래서  “ 이걸 내가 평소 보던 운세랑 연결하면 더 재밌지 않을까?” 하는 생각이 들어서,운세 챗봇을 만들기로 마음먹었습니다.

---

---

## 🎯 프로젝트 개요

| 항목     | 내용                                         |
| ------ | ------------------------------------------ |
| **목표** | 사용자의 입력을 기반으로 GPT가 운세를 분석해주는 챗봇 서비스        |
| **대상** | 일상 속 위로나 조언이 필요한 일반 사용자                    |
| **방식** | FastAPI 백엔드 + HTML/JS/CSS 프론트 + GPT API 연동 |
| **기능** | 챗봇 대화, 결과 저장/조회, 로그인/회원가입                  |

---

## 🛠️ 기술 스택

* **백엔드**: FastAPI, SQLite, httpx
* **프론트엔드**: HTML5, CSS3, JavaScript
* **AI 연동**: [Weniv OpenAI Proxy API](https://dev.wenivops.co.kr/services/openai-api)
* **세션 관리**: 쿠키 기반 로그인

---

## 📦 주요 기능

| 기능         | 설명                                     |
| ---------- | -------------------------------------- |
| 회원가입 / 로그인 | 사용자 인증 및 세션 발급 (`/register`, `/login`) |
| GPT 챗봇     | 운세 분석 및 결과 반환 (`/chat/send`)           |
| 기록 저장      | 대화 및 결과를 DB에 저장 (`/chats`, `/results`) |
| 기록 조회      | 본인의 운세 기록만 보기 (`/my-results`)          |
| 프론트 UI     | 실시간 채팅 인터페이스 구현                        |

---

## 💻 주요 코드 설명

### 📁 `main.py` (FastAPI 백엔드)

* `/chats` : 사용자 질문/응답 메시지를 저장하고 불러오는 API
* `/results` : GPT가 제공한 운세 결과 저장/조회
* `/register`, `/login`, `/logout` : 인증 및 세션 관리
* `/chat/send` : GPT API와 연결되어 응답 생성
* ✅ DB 파일: `chat_logs.db` 자동 생성됨 (SQLite)

---

### 🖼️ `chatbot.html` (운세 챗봇 프론트엔드)

```html
<div class="chat-container">
  <div id="chat-box" class="chat-box"></div>
  <div class="input-area">
    <input type="text" id="user-input" placeholder="운세를 물어보세요..." />
    <button id="send-btn">전송</button>
  </div>
  <div class="button-group" id="result-buttons">
    <button id="result-btn">🔮 운세 결과 보기</button>
    <button id="reset-btn">♻️ 초기화</button>
  </div>
</div>
```

### 🧠 JS 동작 요약

* `sendMessage()` : 사용자 입력 → GPT API POST → 응답 출력
* `fetch('/chats')` : 메시지와 결과 저장
* `sessionStorage.setItem("fortune", answer)` : 결과 임시 저장
* `resetBtn` : 초기 상태로 리셋

---

## 📂 데이터베이스 구조

```sql
-- 사용자 대화 기록
CREATE TABLE chat_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  message TEXT,
  timestamp TEXT
);

-- 운세 결과 저장
CREATE TABLE chat_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  fortune TEXT,
  timestamp TEXT
);
```

---

## 🔐 로그인 & 세션 관리

* 로그인 성공 시 `session_id` 쿠키 발급
* 이후 API 요청에서 해당 세션으로 사용자 식별
* `/my-results` 등은 로그인한 사용자만 접근 가능

---

## ⚙️ 실행 방법

### 1. 가상환경 생성 및 라이브러리 설치

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn httpx jinja2
```

### 2. 실행

```bash
uvicorn main:app --reload
```

* 웹앱 접속: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* API 문서: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📝 회고

| 잘한 점                        | 아쉬운 점                            |
| --------------------------- | -------------------------------- |
| ✅ 세션 기반 로그인 구현 성공           | 🔒 JWT 또는 보안 관련 고려 미흡            |
| ✅ GPT와 실시간 대화 가능            | 🧠 새로고침 시 대화 기록 복원 미구현           |
| ✅ 사용자별 기록 분리 저장             | 📱 모바일 반응형 미지원                   |
| ✅ 예쁜 UI 꾸며봄 (클로버 테마 등)      | 🤖 **AI 의존도가 높아 직접적인 코드 이해 부족**  |
| ✅ 프로젝트 흐름을 따라가며 웹개발 구조를 경험함 | 🧩 복잡한 로직은 AI 없이 다시 구현하려면 어려움 예상 |

---

## 💭 느낀 점

* 처음부터 기획, 설계, API 작성, HTML·JS 연동까지 직접 수행해 보면서 웹 개발의 전체 흐름 을 이해하게 되었습니다.
* 특히 FastAPI와 SQLite를 활용한 서버 구축, RESTful API 구조, 세션 기반 로그인 방식 등이 큰 공부가 되었습니다.
* 그러나 AI와 유튜브를 활용한 코드 작성 의존도가 넌무 높았고 코드 구조나 예외 처리 등에 대한 깊은 이해는 부족했습니다.
* 다음 프로젝트에서는 **직접 더 많이 고민하고 구현하는 방향으로 발전하고 싶습니다.
* 프론트엔드 구성에서도 처음엔 막막했지만, JS 이벤트 처리나 채팅 UI 구성까지 만들어 보면서 자신감을 얻었습니다.
  
---
