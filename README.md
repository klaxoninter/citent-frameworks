# 씨아이텐트 FRAME WORKS

천막·철구조물 정밀자재 산출 및 도면 시스템 (CI TENT 전용)

원본 사이트와 동일한 5개 모듈을 씨아이텐트 브랜드로 재구현한 Streamlit 앱입니다.

## 📋 포함 모듈

1. **맞춤형 트러스 생성기** — 밑더블 삼각 등 8종 트러스 도면·자재산출 (검증 완료: 빗변 6236.2mm)
2. **벽사다리 통합 산출 시스템** — 보강사다리·메인사다리·용마루 통합
3. **프리미엄 평면도 및 원단 야드** — 사다리꼴 평수·원단 야드 산출 (검증 완료: 2.99평)
4. **현장 맞춤형 대각 벽사다리** — PDF/엑셀/CAD(SVG) 다운로드 지원
5. **전문 3D 천막 창고 시뮬레이터** — Plotly 기반 인터랙티브 3D

## 🚀 Streamlit Cloud 배포 방법 (무료)

### 1단계 — GitHub 업로드
1. https://github.com 에 로그인 → **New repository** → 이름 예: `citent-frameworks` → **Create**
2. 다음 4개 파일을 그 저장소에 업로드:
   - `app.py`
   - `requirements.txt`
   - `packages.txt`
   - `README.md`

### 2단계 — Streamlit Cloud 연결
1. https://share.streamlit.io 접속 → GitHub 로그인
2. **Create app** 클릭
3. Repository: 방금 만든 저장소 선택
4. Branch: `main`, Main file path: `app.py`
5. **Deploy** 클릭 → 약 2~3분 후 자동으로 사이트 주소 발급

발급된 URL 예시: `https://citent-frameworks.streamlit.app`

## 🔐 비밀번호

다운로드 비밀번호(공통): **8637** — 사이드바 "고객연락 인증"에 입력

## 🎨 브랜드 커스터마이징

`app.py`에서 다음 값들을 본인 정보로 수정:

```python
# 사이드바 영역
st.caption("제조원: 씨아이텐트(CI TENT)")
st.caption("대표: 최희준")
st.caption("문의: 1644-XXXX")  # ← 실제 번호로 교체
```

특허 출원번호, 비밀번호(현재 `8637`)도 동일하게 검색·교체하시면 됩니다.

## 🛠 로컬 테스트

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 http://localhost:8501 자동 실행

## 📝 한글 폰트

- 1순위: `koreanize-matplotlib` (pip 패키지, OS 무관 작동)
- 2순위: `fonts-nanum` (`packages.txt`로 자동 설치, Streamlit Cloud 환경)

두 가지가 모두 적용되어 있어 어떤 환경에서도 한글이 깨지지 않습니다.

## ⚠️ 참고

- 본 앱은 원본 사이트의 핵심 계산 로직(트러스 빗변·평수·대각길이)을 검증·재구현한 것입니다.
- 실제 시공·견적용으로 사용하실 경우 자체 검증 후 사용해 주세요.
