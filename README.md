# Lazyest Skills — implementation preparation

짧은 구현 시간에 작동하는 최소 기능을 만들고 증거로 검증하는 공개 스킬입니다. 준비용 묶음은 `prep/hynix-20261031` 브랜치에 둡니다. 실제 과제와 답안은 이 저장소에 올리지 않습니다.

`ship-small`은 요구 파악 → 구현 → 검증을 짧게 연결합니다. 인터뷰·조사·데이터·보안·고장·제출 참조는 해당 조건이 있을 때만 읽습니다. 작은 수정에 별도 계획이나 다중 에이전트를 강제하지 않습니다. [공식 자료 22개와 설계 근거](RESEARCH.md)를 함께 확인할 수 있습니다.

## 설치

아래 브랜치를 내려받고, 실제 작업 프로젝트 루트에서 설치합니다. 기존 스킬은 덮어쓰지 않습니다. Python 3 표준 라이브러리만 사용합니다. 원격 URL·브랜치가 실제 공개되어 있는지는 접속으로 확인하세요.

```sh
git clone --branch prep/hynix-20261031 --single-branch https://github.com/lazyest-hyun/lazyest-skills.git /tmp/lazyest-skill-prep
python3 /tmp/lazyest-skill-prep/scripts/install.py --project .
```

`.agents/skills/ship-small/SKILL.md`가 만들어집니다. Codex를 새 세션으로 열어 `$ship-small`로 명시 호출합니다. 자동 선택은 모델·환경에 따라 달라지므로 실제 작업 전에 확인하세요. AI 사용이 금지된 단계에서는 호출하지 않습니다.

제공된 Codex 버전에서 `/skills` 또는 스킬 목록으로 발견 여부를 확인하세요. 발견되지 않으면 업데이트하지 말고 필요한 `skills/ship-small/SKILL.md` 하나를 직접 읽도록 요청하세요. 읽기 fallback은 자동 트리거 성공을 뜻하지 않습니다. 시험 환경에서는 개인 키·개인 파일 업로드·과제 외부 전송·git push·외부 배포를 하지 않습니다. 제출 확정 후 AI 금지 서술형 답안 생성·윤문에도 사용하지 않습니다.

Computer Use 금지 환경에서는 브라우저·데스크톱 자동 조작을 사용하지 않습니다. 허용된 CLI 검사와 사용자의 내장 미리보기 직접 점검을 구분합니다. 외부 코딩 에이전트나 별도 모델에도 연결하지 않습니다.

예: “180분 안에 제공된 앱에 CSV 업로드와 합계 표시를 구현하고 확인해줘.”
비예: “오늘 날씨 알려줘”, “이 문장만 다듬어줘”.

## 로컬 검사

```sh
python3 tests/check.py
python3 tests/forward-fixtures.py
python3 -m unittest discover -s tests/fixtures -p 'test_*.py' -v
python3 scripts/scan-history.py
```

첫 검사는 파일 구조·상대 링크·비밀값 패턴·설치 smoke를 확인합니다. 두 번째 검사는 합성 제목 수정과 저장 유실 재현·수정의 CLI 검증입니다. [독립 native 평가 기록](tests/evidence/native-forward.md)에 메타데이터 판단 8건과 행동 시뮬레이션 10건 및 한계를 구분했습니다. 제공된 시험 Codex의 발견·자동 선택 성공은 아직 확인하지 않았습니다. 유료 모델 호출은 포함하지 않습니다.

추가 합성 데이터 계약 검사 5개는 ID 경계, null/누락/0/문자열, 행 오류, 공급자 단일 원본을 확인합니다. 설치 파일은 런타임에 네트워크나 외부 모델을 호출하지 않습니다. 공개 자료 허용은 모든 도구·업로드·외부 전송을 허용한다는 뜻이 아니므로 실제 제공 안내를 우선하세요. 결과 발표까지 이 준비 브랜치를 공개 상태로 유지하고, 실제 시험 내용은 공개하지 않습니다.
