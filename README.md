# 🌐 Browser Engine from Scratch

[Web Browser Engineering](https://browser.engineering/) 교재를 기반으로 Python으로 웹 브라우저 엔진을 처음부터 구현하는 프로젝트입니다.

HTTP 요청, HTML 파싱, 레이아웃, 렌더링까지 브라우저의 핵심 동작을 직접 만들어보며 웹이 어떻게 동작하는지 이해하는 것이 목표입니다.

## 시작하기

### 요구사항

- Python 3.12+
- pip
- pytest

### 설치

```bash
git clone <repo-url>
cd browser-engine

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 실행

```bash
# 기본 실행
python src/browser.py http://example.org/

# file 스킴
python src/browser.py file:///path/to/local.html

# data 스킴
python src/browser.py "data:text/html,Hello world!"

# view-source
python src/browser.py view-source:http://example.org/
```

### 테스트

```bash
# 전체 테스트
pytest

# 특정 챕터
pytest tests/test_ch01.py -v

# 특정 연습문제
pytest tests/test_ch01.py::test_entities -v
```

## 프로젝트 구조

```
browser-engine/
├── README.md              # 프로젝트 소개 (이 문서)
├── claude.md              # Claude 협업 가이드
├── requirements.txt
├── src/
│   └── browser.py         # 메인 브라우저 코드
├── tests/
│   ├── conftest.py        # 공통 fixture
│   └── test_ch01.py       # 챕터별 테스트
└── fixtures/              # 테스트용 정적 파일
```

## 챕터 진행 현황

| 챕터 | 주제 | 상태 |
|------|------|------|
| 1 | Downloading Web Pages | ⬜ |
| 2 | Drawing to the Screen | ⬜ |
| 3 | Formatting Text | ⬜ |
| 4 | Constructing an HTML Tree | ⬜ |
| 5 | Laying Out Pages | ⬜ |

## 참고 자료

- 교재: https://browser.engineering/