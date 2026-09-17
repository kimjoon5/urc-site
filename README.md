# URC 사이트

연세대학교 도시공학과 대체투자학회 URC 홈페이지. 빌드 도구 없이 정적 HTML/CSS/JS로만 구성되어 GitHub Pages에 바로 올라갑니다.

## 페이지

| 경로 | 내용 |
|---|---|
| `index.html` | Home |
| `about-us/` | Introduction · Greetings |
| `curriculum/` | Sessions (4개) · External Activities · Networking |
| `research/` | Market · Issue · REITs Report |
| `network/` | Advisors · Members (Founders~6th) · URC Network |
| `join-us/` | Recruitment · FAQ |

모든 페이지는 100vh 섹션의 연속입니다. 첫 섹션이 히어로, 마지막 섹션이 Contact이고, 휠 한 번 / 방향키 / 오른쪽 점을 눌러 섹션 단위로 이동합니다. 세로로 긴 섹션(Members 등)은 안에서 자연스럽게 스크롤됩니다.

## 구성

```
data/*.json           페이지 내용. 여기만 고치면 됩니다
tools/build.py        data → 모든 index.html 생성
assets/css/style.css  스타일 (Pretendard 단일 서체, 네이비·슬레이트 팔레트)
assets/js/main.js     네비게이션 · 섹션 스크롤 · 리빌 · 기수 전환
assets/img/           사진·로고
```

## 내용 수정하기

1. `data/` 안의 JSON을 수정합니다. 예: 멤버 추가는 `data/network.json` 의 `members` 에 항목을 넣고 사진을 `assets/img/` 에 넣습니다.
2. 아래 명령으로 HTML을 다시 만듭니다. Python 3만 있으면 됩니다.

```bash
python3 tools/build.py
```

3. 커밋 후 푸시하면 끝입니다.

## 배포 (GitHub Pages)

저장소 → **Settings → Pages** → Branch `main` / `/ (root)`. 모든 경로가 상대 경로라 하위 경로 배포도 문제 없습니다.

## 로컬에서 보기

```bash
python3 -m http.server 8000
# http://localhost:8000
```
