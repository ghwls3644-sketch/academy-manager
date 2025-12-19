# Docker 개발 환경 가이드

이 문서는 Docker를 사용하여 모든 개발 PC(Windows, Linux, Mac)에서 동일한 환경으로 개발하는 방법을 설명합니다.

---

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [개발 PC 초기 설정](#개발-pc-초기-설정-windows)
3. [일상적인 개발 작업](#일상적인-개발-작업)
4. [서버에서 코드 반영](#서버에서-코드-반영)
5. [다른 개발 PC에서 동기화](#다른-개발-pc에서-동기화)
6. [자주 사용하는 명령어](#자주-사용하는-명령어)
7. [문제 해결](#문제-해결)

---

## 사전 요구사항

- **Docker Desktop** 설치 필수
  - Windows: https://docs.docker.com/desktop/install/windows-install/
  - Mac: https://docs.docker.com/desktop/install/mac-install/
  - Linux: https://docs.docker.com/desktop/install/linux-install/
- **Git** 설치

---

## 개발 PC 초기 설정 (Windows)

> 기존에 작업 중인 프로젝트 폴더가 있는 경우

### 1단계: 최신 코드 가져오기

```powershell
# 1. 프로젝트 폴더로 이동
cd D:\Project\academy_saas

# 2. GitHub에서 최신 코드 가져오기
git pull
```

### 2단계: 환경변수 파일 설정

`.env` 파일에서 `DB_HOST`를 Docker 컨테이너 이름으로 변경:

```diff
# 기존 (로컬용)
- DB_HOST=127.0.0.1

# Docker용으로 변경
+ DB_HOST=db
```

### 3단계: 기존 가상환경 삭제 (선택)

Docker 사용 시 가상환경이 불필요하므로 삭제 가능:

```powershell
# .venv 폴더 삭제 (용량 확보)
Remove-Item -Recurse -Force .venv
```

### 4단계: Docker 시작

```powershell
# Docker Desktop이 실행 중인지 확인 후
docker compose up --build
```

> 첫 실행 시 이미지 빌드로 몇 분 소요됩니다.

### 5단계: 데이터베이스 마이그레이션

**새 터미널**을 열고:

```powershell
cd D:\Project\academy_saas
docker compose exec web python manage.py migrate
```

### 6단계: 슈퍼유저 생성 (초기 설정 시)

초기 설정 시 관리자 계정이 필요합니다:

```powershell
docker compose exec web python manage.py createsuperuser
```

프롬프트에 따라 사용자명, 이메일, 비밀번호를 입력합니다.

> **참고**: 데이터베이스 볼륨이 유지되면 슈퍼유저도 보존됩니다. `docker compose down -v`를 사용하면 볼륨까지 삭제되어 데이터가 초기화됩니다.

### 7단계: 브라우저에서 확인

http://localhost:8000 접속

---

## 일상적인 개발 작업

### 개발 서버 시작

```powershell
# Docker Desktop이 실행 중인지 확인 후
cd D:\Project\academy_saas
docker compose up
```

> 백그라운드 실행: `docker compose up -d`

### 코드 수정

코드를 수정하면 Django 서버가 자동으로 재시작됩니다. (핫 리로드)

### 작업 완료 후 커밋 및 푸시

```powershell
# 1. 변경사항 확인
git status

# 2. 변경사항 스테이징
git add .

# 3. 커밋
git commit -m "작업 내용 설명"

# 4. GitHub에 푸시
git push
```

### 개발 서버 종료

```powershell
docker compose down
```

---

## 서버에서 코드 반영

> 개발 PC에서 푸시한 코드를 서버에 반영하는 방법

### 1단계: 최신 코드 가져오기

```bash
cd /home/makist/Project/academy_saas
git pull
```

### 2단계: 마이그레이션 적용

**방법 A: Docker를 사용하는 경우**

```bash
docker compose exec web python manage.py migrate
```

**방법 B: 가상환경을 사용하는 경우 (현재 서버)**

```bash
source .venv/bin/activate
python manage.py migrate
```

### 3단계: 서버 재시작 (필요 시)

Django 개발 서버는 코드 변경 시 자동 재시작됩니다.
변경이 반영되지 않으면 서버를 수동 재시작하세요.

---

## 다른 개발 PC에서 동기화

> 개발 PC A에서 푸시한 코드를 개발 PC B에서 가져오는 방법

### 1단계: 최신 코드 가져오기

```powershell
cd D:\Project\academy_saas
git pull
```

### 2단계: 이미지 재빌드 (패키지 변경 시)

`requirements.txt`가 변경되었다면:

```powershell
docker compose build
```

### 3단계: 마이그레이션 적용

```powershell
docker compose exec web python manage.py migrate
```

### 4단계: 개발 서버 시작

```powershell
docker compose up
```

---

## 자주 사용하는 명령어

| 작업 | 명령어 |
|------|--------|
| 서버 시작 | `docker compose up` |
| 서버 시작 (백그라운드) | `docker compose up -d` |
| 서버 중지 | `docker compose down` |
| 마이그레이션 | `docker compose exec web python manage.py migrate` |
| 마이그레이션 생성 | `docker compose exec web python manage.py makemigrations` |
| Django 쉘 | `docker compose exec web python manage.py shell` |
| 슈퍼유저 생성 | `docker compose exec web python manage.py createsuperuser` |
| 이미지 재빌드 | `docker compose build` |
| 컨테이너 상태 확인 | `docker compose ps` |
| 로그 확인 | `docker compose logs -f` |

---

## 문제 해결

### 데이터베이스 연결 오류

```
django.db.utils.OperationalError: connection refused
```

**해결 방법**:
```powershell
# 컨테이너 상태 확인
docker compose ps

# 데이터베이스가 실행 중이 아니면 재시작
docker compose up -d db
```

### 포트 충돌 오류

```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**해결 방법**:
1. 기존에 실행 중인 Django 서버를 종료하거나
2. `docker-compose.yml`에서 포트 변경:
   ```yaml
   ports:
     - "8001:8000"  # 8001로 변경
   ```

### 패키지 설치 후 반영되지 않음

```powershell
# 이미지 재빌드 필요
docker compose build
docker compose up
```

---

## 개발 워크플로우 요약

```
┌─────────────────────────────────────────────────────────────────┐
│                        개발 PC A (Windows)                       │
│  1. docker compose up                                            │
│  2. 코드 수정                                                     │
│  3. git add . → git commit → git push                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     GitHub      │
                    └─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│      서버 (Ubuntu)         │   │    개발 PC B (Windows)     │
│  1. git pull              │   │  1. git pull              │
│  2. python manage.py      │   │  2. docker compose build  │
│     migrate               │   │  3. docker compose exec   │
│                           │   │     web python manage.py  │
│                           │   │     migrate               │
│                           │   │  4. docker compose up     │
└───────────────────────────┘   └───────────────────────────┘
```

---

## 기존 방식과의 비교

| 항목 | 기존 (가상환경) | Docker |
|------|----------------|--------|
| 가상환경 활성화 | OS마다 다름 | 불필요 ✅ |
| Python 버전 관리 | 수동 설치 | 자동 (이미지에 포함) ✅ |
| PostgreSQL 설치 | 각 PC에 설치 | 자동 (컨테이너) ✅ |
| 환경 통일성 | 보장 안 됨 | 완벽히 동일 ✅ |
