@echo off
chcp 65001 > nul
echo Git Pre-commit Hook 설치 중...

copy /Y "scripts\pre-commit" ".git\hooks\pre-commit"

if errorlevel 1 (
    echo [오류] Hook 설치 실패!
    pause
    exit /b 1
)

echo [성공] Pre-commit Hook이 설치되었습니다!
echo 이제 git commit 할 때마다 자동으로 데이터가 백업됩니다.
pause
