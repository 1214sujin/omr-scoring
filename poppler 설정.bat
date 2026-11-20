@echo off
chcp 65001 > nul

set "TARGET_DIR=%~dp0poppler\Library\bin"

if exist "%TARGET_DIR%" (
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $target = $env:TARGET_DIR; $oldPath = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($oldPath -notlike '*'+$target+'*') { [Environment]::SetEnvironmentVariable('Path', $oldPath + ';' + $target, 'User'); [System.Windows.Forms.MessageBox]::Show('환경 변수(PATH) 설정이 완료되었습니다.', '설정 완료', 'OK', 'Information'); } else { [System.Windows.Forms.MessageBox]::Show('이미 환경 변수가 등록되어 있습니다.', '알림', 'OK', 'Information'); }"
) else (
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('poppler 폴더를 찾을 수 없습니다.' + [Environment]::NewLine + '압축을 푼 폴더 안에서 실행해 주세요.', '오류 발생', 'OK', 'Error')"
)

exit
