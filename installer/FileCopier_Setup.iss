; Inno Setup 스크립트 — FileCopier 설치 프로그램
; 빌드 전 준비: dist/FileCopier.exe 와 icon.ico 가 프로젝트 루트에 있어야 합니다.
; 컴파일: Inno Setup Compiler 로 이 파일을 열고 빌드하세요.
; 다운로드: https://jrsoftware.org/isdl.php

#define AppName "FileCopier"
#define AppVersion "1.0.0"
#define AppPublisher "your-name"
#define AppExeName "FileCopier.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=..\installer_output
OutputBaseFilename=FileCopier_Setup_v{#AppVersion}
SetupIconFile=..\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 관리자 권한 불필요 — 사용자 폴더에 설치
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 아이콘:"

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{#AppName} 제거"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "설치 완료 후 바로 실행"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
