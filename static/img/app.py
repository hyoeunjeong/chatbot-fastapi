from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용, 또는 ["http://localhost:3000"] 등 특정 도메인만 허용 가능
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST 등)
    allow_headers=["*"],  # 모든 헤더 허용
)
