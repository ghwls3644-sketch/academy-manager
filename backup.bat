@echo off
chcp 65001 > nul
echo ===================================
echo   학원 관리 시스템 데이터 백업
echo ===================================
echo.

REM Docker 컨테이너 확인
docker ps | findstr academy_web > nul
if errorlevel 1 (
    echo [오류] academy_web 컨테이너가 실행 중이 아닙니다.
    echo Docker Compose를 먼저 실행해주세요: docker-compose up -d
    pause
    exit /b 1
)

echo [1/3] 데이터 백업 중...
docker exec academy_web python manage.py dumpdata --indent 2 -o data_backup.json

if errorlevel 1 (
    echo [오류] 백업 실패!
    pause
    exit /b 1
)

echo [2/3] UTF-8 인코딩 확인...
docker exec academy_web python -c "import json; d=json.load(open('data_backup.json','r',encoding='utf-8')); print(f'총 {len(d)}개 레코드 백업됨')"

echo [3/3] 백업 완료!
echo.
echo 백업 파일: data_backup.json
echo 시간: %date% %time%
echo ===================================
pause
