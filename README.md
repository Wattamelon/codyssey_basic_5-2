# 코디세이 미션 5-2 — 나의 메모 앱

FastAPI와 SQLAlchemy로 구현한 메모 CRUD 웹 서비스입니다. Jinja2 기반 SSR 화면에서 메모를 등록·조회·수정·삭제하고 SQLite에 저장합니다.

## 주요 기능

- 앱 소개 및 목록·등록 링크가 있는 홈 화면
- 메모 목록, 상세, 등록 폼, 수정 폼
- HTML Form과 POST를 통한 등록·수정·삭제
- 정상 변경 처리 후 303 Redirect를 사용하는 PRG 흐름
- 서버 재시작 후에도 유지되는 DB 저장
- 없는 메모 안내와 제목·내용 입력 검증

로그인·인증·권한, 모델 간 관계와 검색 기능은 구현하지 않습니다.

## 사용 기술

Python 3.10 이상과 다음 라이브러리를 사용합니다. 버전 범위는 `requirements.txt`에서 관리합니다.

| 기술 | 역할 |
|---|---|
| FastAPI | 라우팅, Form 입력, 의존성 주입 |
| Uvicorn | ASGI 서버 |
| SQLAlchemy 2.0 | ORM 모델과 DB CRUD |
| SQLite | 파일 기반 데이터 저장 |
| Jinja2 | HTML 템플릿 렌더링 |
| python-multipart | 폼 데이터 파싱 지원 |

## 설치 및 실행

`main.py`와 `requirements.txt`가 있는 프로젝트 폴더에서 실행합니다.

### 1. 가상환경

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 패키지 설치

```bash
python -m pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python -m uvicorn main:app --reload --port 8000
```

터미널에서 `Application startup complete.`를 확인하고 접속합니다.

- 홈: http://localhost:8000
- 목록: http://localhost:8000/memos
- 등록: http://localhost:8000/memos/new
- 자동 API 문서: http://localhost:8000/docs

`--reload`는 Python 파일 변경 시 개발 서버를 재시작합니다. 종료는 `Ctrl+C`입니다. 새 터미널에서는 가상환경 활성화 후 서버를 다시 실행합니다.

첫 실행 시 프로젝트 폴더에 `database.db`와 `memos` 테이블이 자동 생성됩니다. 예제 데이터를 자동 삽입하지 않으므로 새 DB는 빈 목록으로 시작합니다. 별도 DB 서버나 환경변수 설정은 필요하지 않습니다.

## 사용 방법

1. 홈에서 **새 메모 작성**을 선택하고 제목·내용을 저장합니다.
2. 목록에서 제목을 클릭해 상세 내용을 확인합니다.
3. 상세의 **수정**으로 기존 내용을 변경하거나 **삭제** 버튼을 누릅니다.
4. 등록·수정 폼의 **취소**는 저장 없이 목록으로 이동합니다.

## 프로젝트 구조

```text
5-2/
├── main.py                       # 앱 생성, 시작 시 DB 초기화, 라우터 등록
├── database.py                   # Engine, Session, get_db, Base
├── requirements.txt              # 의존성 목록
├── models/
│   └── memo.py                   # Memo ORM 모델
├── repositories/
│   └── memo_repository.py        # DB 조회·저장·수정·삭제
├── services/
│   └── memo_service.py           # 입력 검증, 처리 흐름, MemoData 변환
├── routers/
│   └── memo.py                   # HTTP 요청·응답과 화면 전환
├── templates/
│   ├── home.html
│   ├── memo_list.html
│   ├── memo_detail.html
│   ├── memo_create.html
│   ├── memo_edit.html
│   ├── memo_not_found.html
│   └── new_placeholder.html      # 이전 학습용, 현재 사용하지 않음
├── study_notes/                  # 단계별 학습 자료
└── database.db                   # 실행 시 생성, Git 추적 제외
```

각 Python 패키지에는 `__init__.py`가 포함되어 있습니다.

## 요청 처리 구조

```text
브라우저 → Router → Service → Repository → SQLAlchemy → SQLite
```

조회 결과는 Repository → Service → Router 순서로 돌아옵니다. Service는 ORM 객체를 `MemoData`로 변환하고, Router는 context를 통해 Jinja2에 전달하여 HTML을 응답합니다.

`Depends(get_db)`로 DB를 사용하는 요청에 Session을 제공합니다. `get_db()`는 Session을 열어 yield로 전달하고 사용이 끝나면 닫습니다. 변경 사항의 commit은 Repository에서 수행합니다.

## 서버를 실행하면 코드가 어떻게 움직일까?

```bash
python -m uvicorn main:app --reload --port 8000
```

이 명령의 흐름은 **서버 시작 때 한 번 준비하는 과정**과 **브라우저가 요청할 때마다 처리하는 과정**으로 나누어 보면 이해하기 쉽습니다.

### 1. Uvicorn이 main.py의 app을 찾습니다

| 명령 부분 | 의미 |
|---|---|
| `python -m uvicorn` | 현재 Python 환경에서 Uvicorn 서버 프로그램 실행 |
| `main:app` | main 모듈을 불러오고, 그 안의 app 객체를 사용 |
| `--reload` | 개발 중 코드 변경을 감시하고 서버 프로세스를 재시작 |
| `--port 8000` | 8000번 포트에서 요청 대기 |

먼저 실행되는 프로그램은 Uvicorn입니다. Uvicorn이 `main.py`를 import하면서 우리 앱 코드가 실행됩니다. `main:app`은 파일 경로 문자열이 아니라 **모듈 이름:객체 이름**입니다.

### 2. main.py의 import를 따라 필요한 파일을 읽습니다

main.py에는 다음 코드가 있습니다.

```python
from database import initialize_database
from routers.memo import router
```

첫 줄에서 Python은 `database.py`를 불러옵니다. 파일 최상위 코드를 실행하면서 다음을 준비합니다.

- `PROJECT_DIR`: 프로젝트 폴더 경로
- `engine`: 프로젝트의 database.db에 접근할 연결 설정
- `SessionLocal`: Session을 생성하는 도구
- `Base`: ORM 모델의 공통 기반
- `get_db`, `initialize_database`: 함수 정의

**함수를 정의하는 것과 호출하는 것은 다릅니다.** 이 import만으로 get_db가 Session을 생성하거나 initialize_database가 테이블을 만드는 것은 아닙니다. Engine도 생성 시점에 즉시 DB 작업을 수행하는 것이 아니라 실제 작업에 필요한 연결을 준비합니다.

둘째 줄에서는 아래 import 연결을 따라갑니다.

```text
main.py
  └─ routers/memo.py
       └─ services/memo_service.py
            └─ repositories/memo_repository.py
                 └─ models/memo.py
                      └─ database.py의 Base 사용
```

`models/memo.py`를 읽으면 Memo 클래스의 테이블 이름과 열 정보가 Base의 metadata에 등록됩니다. 여기서도 실제 행을 저장하지는 않습니다. 이미 import한 database 모듈은 같은 프로세스에서 보통 재사용하므로 이 경로를 따라 Engine이 계속 새로 생성되는 것은 아닙니다.

`routers/memo.py`에서는 APIRouter와 Jinja2Templates 객체를 만들고, `@router.get(...)`, `@router.post(...)`로 경로와 함수의 연결을 등록합니다. **등록 시점에는 home이나 create_memo 같은 함수의 본문을 실행하지 않습니다.**

### 3. FastAPI 앱을 만들고 라우터를 붙입니다

main.py의 다음 코드가 실행됩니다.

```python
app = FastAPI(lifespan=lifespan)
app.include_router(router)
```

첫 줄은 FastAPI 앱 객체를 만들고, 시작·종료 시 사용할 lifespan을 연결합니다. 둘째 줄은 Router에 등록한 경로들을 app에 포함합니다. 이제 app은 GET `/`, POST `/memos` 등을 어떤 함수로 처리할지 알고 있습니다.

이 시점에도 브라우저가 요청하지 않았으므로 홈 화면을 렌더링하거나 메모를 등록하지 않습니다.

### 4. 서버 시작 단계에서 DB를 초기화합니다

Uvicorn이 앱의 시작 처리를 진행하면 다음 lifespan 코드가 실행됩니다.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield
```

`@asynccontextmanager`는 이 함수를 앱의 시작·종료 범위에서 사용하도록 돕습니다. `yield` 앞은 시작 준비, 뒤는 종료 정리 코드를 둘 자리입니다. 현재 코드는 yield 뒤에 별도 정리 작업이 없습니다.

호출 관계는 다음과 같습니다.

```text
main.py: lifespan
  → database.py: initialize_database
  → Memo 모델 import 확인
  → Base.metadata.create_all(engine)
  → SQLite의 database.db와 없는 테이블 준비
```

모델을 import해야 Base가 어떤 테이블을 만들지 알 수 있습니다. 현재는 앞선 import 과정에서도 Memo가 등록되지만, 초기화 함수 자체에서도 모델을 가져오도록 명시되어 있습니다.

`create_all()`은 테이블이 이미 있으면 유지합니다. 매번 데이터를 지우고 다시 만드는 동작이 아닙니다. 이 준비가 완료되면 앱은 시작 완료 상태가 되고 요청을 기다립니다.

### 5. 홈 접속: DB를 거치지 않는 요청

브라우저 주소창에 `http://localhost:8000/`를 입력하면 GET `/` 요청이 발생합니다.

```text
브라우저 GET /
  → Uvicorn → FastAPI app
  → routers/memo.py: home(request)
  → render(request, "home.html", context)
  → templates/home.html에 앱 이름·소개 문장 적용
  → HTML 응답 → 브라우저 표시
```

home은 DB 데이터를 사용하지 않으므로 Service·Repository·get_db를 호출하지 않습니다. 모든 요청이 항상 모든 계층을 거치는 것은 아닙니다.

### 6. 목록 접속: 요청이 DB까지 가는 과정

홈에서 목록 링크를 클릭하면 GET `/memos` 요청이 발생합니다.

```python
@router.get("/memos")
def list_memos(request: Request, db: Session = Depends(get_db)):
    return render(request, "memo_list.html", {"memos": service.list_memos(db)})
```

FastAPI는 이 함수를 실행하기 전에 `Depends(get_db)`에 필요한 값을 준비합니다.

1. `database.py`의 get_db를 진행합니다.
2. `SessionLocal()`로 이번 요청에서 사용할 Session을 만듭니다.
3. `yield db`로 제공한 Session을 목록 함수의 db 매개변수에 전달합니다.
4. 목록 함수가 그 Session으로 Service를 호출합니다.

```text
routers/memo.py: list_memos(request, db)
  → services/memo_service.py: list_memos(db)
  → repositories/memo_repository.py: list_memos(db)
  → select(Memo).order_by(Memo.id)
  → db.scalars(...).all()
  → SQLite의 memos 테이블 조회
```

Repository가 반환하는 것은 Memo ORM 객체들의 목록입니다. Service는 각 객체를 `to_data()`로 변환하여 `MemoData` 목록을 반환합니다.

```text
DB의 행
  → Repository: Memo 객체 목록
  → Service: MemoData 목록
  → Router: context의 memos에 담음
  → render → TemplateResponse
  → memo_list.html의 for문으로 제목·상세 링크 생성
  → HTML 응답
```

현재 Depends의 yield 의존성 기본 범위에서는 정상 응답 전송 후 FastAPI가 get_db의 정리를 진행하고, with 블록이 Session을 닫습니다. Router가 Session을 매번 직접 닫을 필요가 없는 이유입니다. Session을 닫는 것과 변경을 commit하는 것은 별개입니다.

### 7. 메모 등록: 저장 후 새로운 조회 요청으로 이어집니다

먼저 GET `/memos/new`가 등록 HTML을 보여줍니다. 이 화면을 여는 것만으로 저장하지는 않습니다.

사용자가 저장을 누르면 HTML의 설정에 따라 요청이 발생합니다.

```html
<form method="post" action="/memos">
```

```text
브라우저 POST /memos (title, content)
  → FastAPI가 Form으로 입력을 받고 get_db로 Session 준비
  → Router의 create_memo
  → Service의 create_memo
       → validate: 앞뒤 공백 제거, 빈값·제목 길이 확인
  → Repository의 create_memo
       → Memo 객체 생성
       → db.add: 저장 대상으로 등록
       → db.commit: 변경 확정
       → db.refresh: 저장된 값 다시 읽기
  → Service가 MemoData 반환
  → Router가 redirect_to_list 호출
  → 303 응답, Location: /memos
```

303을 받은 **브라우저가 새 GET `/memos` 요청을 보냅니다.** 저장 함수가 목록 함수를 직접 호출하는 것이 아닙니다. 이 GET은 위의 목록 조회 과정을 다시 거칩니다.

입력 검증 실패 시에는 Repository 저장으로 진행하지 않고, Router가 입력값·오류 문구를 담은 등록 폼을 422로 렌더링합니다.

### 8. 상세·수정·삭제도 같은 구조로 처리합니다

| 요청 | Service·Repository의 주요 작업 | 응답 |
|---|---|---|
| GET `/memos/1` | get_memo → db.get(Memo, 1) | 상세 HTML 또는 404 안내 |
| GET `/memos/1/edit` | 같은 ID 조회 | 기존 값이 채워진 수정 HTML 또는 404 |
| POST `/memos/1/edit` | 대상 조회 → 입력 검증 → 속성 변경 → commit | 303 목록 이동, 검증 실패는 422 폼 |
| POST `/memos/1/delete` | 대상 조회 → db.delete → commit | 303 목록 이동 |

실제 요청에서는 주소의 1이 memo_id로 전달됩니다. 수정·삭제의 대상이 없으면 변경 없이 목록으로 이동합니다. 여러 함수가 같은 DB와 Engine을 사용하지만 작업용 Session은 요청 범위로 관리합니다.

### 9. 새로고침·코드 변경·서버 종료는 서로 다릅니다

| 행동 | 다시 실행되는 것 |
|---|---|
| 브라우저 목록 새로고침 | GET `/memos` 처리 함수와 조회 흐름 |
| Python 코드 변경으로 reload | 서버 프로세스가 다시 시작되어 import·앱 생성·lifespan 준비 반복 |
| Ctrl+C | Uvicorn이 앱 종료 흐름을 진행하고 서버 종료 |

브라우저 새로고침마다 main.py 전체가 실행되는 것은 아닙니다. 또한 서버가 재시작되어도 이미 commit된 SQLite 데이터는 파일에 남습니다. `--reload`는 코드 감시 옵션이며 브라우저 화면을 자동 새로고침하는 옵션은 아닙니다.

### 전체 흐름 요약

```text
[서버 시작]
Uvicorn 실행
  → main.py import
  → DB 설정·모델·Service·Repository·Router 준비
  → FastAPI app 생성 및 라우터 포함
  → lifespan → DB 테이블 초기화
  → 요청 대기

[요청 처리]
브라우저 요청
  → FastAPI가 경로·방식에 맞는 Router 함수 선택
  → 필요한 경우 Depends로 Session 준비
  → Service → Repository → SQLite
  → 결과를 Service → Router로 전달
  → HTML 렌더링 또는 303 응답
  → 요청 Session 정리
```

## CRUD URL

| 방식 | 경로 | 기능 |
|---|---|---|
| GET | `/` | 홈 |
| GET | `/memos` | 목록 |
| GET | `/memos/new` | 등록 폼 |
| POST | `/memos` | 등록 처리 |
| GET | `/memos/{memo_id}` | 상세 |
| GET | `/memos/{memo_id}/edit` | 수정 폼 |
| POST | `/memos/{memo_id}/edit` | 수정 처리 |
| POST | `/memos/{memo_id}/delete` | 삭제 처리 |

고정 경로 `/memos/new`를 매개변수 경로보다 먼저 등록합니다.

### PRG 및 예외 처리

```text
POST → DB 변경 및 commit → 303 Redirect → GET /memos
```

정상 처리 후 목록에서 새로고침하면 GET 조회만 반복합니다. 이 흐름은 직전 POST의 재제출을 피하며, 빠른 중복 클릭 등 모든 중복 요청을 방지하는 장치는 아닙니다.

- 제목·내용의 앞뒤 공백을 제거하고 빈값을 거부합니다.
- 제목은 최대 100자이며, 실패 시 입력값과 안내 문구가 있는 폼을 422로 응답합니다.
- 없는 ID의 상세·수정 GET은 안내 HTML과 404를 응답합니다.
- 없는 ID의 수정·삭제 POST는 변경 없이 303으로 목록에 이동합니다.
- 정수가 아닌 ID는 FastAPI가 422 검증 오류로 처리합니다.

## 데이터 모델과 저장

테이블 이름은 `memos`입니다.

| 필드 | 의미 |
|---|---|
| id | 정수 기본 키 |
| title | 제목, 서비스에서 100자 이하 검증 |
| content | 메모 내용 |
| created_at | 생성 시 기록하는 작성일시 |

작성일시는 서버 로컬 시간을 사용하고 수정할 때 유지됩니다. 상세 화면에는 전체 필드가 표시됩니다.

DB 경로는 `database.py` 위치를 기준으로 결정합니다. DB 파일은 `.gitignore`로 제외되므로 저장소를 새로 받으면 자신의 빈 DB가 생성됩니다. 테이블 초기화의 `create_all()`은 기존 테이블 구조를 자동 변경하지 않습니다.

### DB 직접 조회

서버를 한 번 실행한 뒤 프로젝트 폴더에서 다음 명령으로 저장 내용을 확인합니다. Python 표준 sqlite3를 사용하며 DB를 읽기 전용으로 엽니다.

```bash
python -c "import sqlite3; db = sqlite3.connect('file:database.db?mode=ro', uri=True); print(db.execute('SELECT id, title, content, created_at FROM memos ORDER BY id').fetchall()); db.close()"
```

## 기능 확인 순서

아래 항목은 실행 후 직접 확인할 수 있습니다.

- 홈의 링크와 빈 목록 안내 확인
- 메모 등록 후 목록·상세의 제목·내용·작성일시 확인
- 수정 후 ID·작성일시는 유지되고 제목·내용만 바뀌는지 확인
- 삭제 후 목록에서 사라지고 해당 상세 주소가 404인지 확인
- 로그에서 변경 POST 303 다음 목록 GET 200 확인
- 목록 새로고침으로 메모가 중복 등록되지 않는지 확인
- 서버 종료·재실행 후 저장한 메모가 유지되는지 확인
- 공백만 있는 입력과 100자를 넘는 제목이 거부되는지 확인

## 실행 문제 확인

| 증상 | 확인할 내용 |
|---|---|
| 패키지를 찾지 못함 | 가상환경 활성화 및 requirements.txt 설치 |
| main 모듈 import 실패 | main.py가 있는 폴더에서 서버 실행 |
| 8000 포트 사용 중 | 이전 서버가 실행 중인지 확인하고 해당 터미널에서 종료 |
| 새 환경의 목록이 비어 있음 | DB 파일은 Git에 포함되지 않음 |
| 폼 제출 후 422 | 필수값·제목 길이·필드 이름 확인 |
