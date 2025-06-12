from pydantic import BaseModel

# 📥 회원가입 시 받는 데이터 구조
class UserCreate(BaseModel):
    username: str      # 사용자명
    email: str         # 이메일 주소
    password: str      # 비밀번호 (원본)

# 🔐 로그인 시 받는 데이터 구조
class UserLogin(BaseModel):
    username: str      # 사용자명
    password: str      # 비밀번호

# 🗃 실제 내부 저장용 사용자 모델
class User(BaseModel):
    id: int                    # 고유 사용자 ID
    username: str              # 사용자명
    email: str                 # 이메일
    hashed_password: str       # 암호화된 비밀번호

# 📤 응답에 사용할 공개 사용자 정보 (비밀번호 제외)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
