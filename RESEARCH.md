# 설계 근거

2026-10-30 확인한 공개 1차 자료입니다. 아래 적용은 이 저장소의 설계 판단이며, 특정 시험 문제·규칙의 출처를 공개하는 문서가 아닙니다. 다른 제공 환경의 실제 지침이 우선합니다.

| 공식 자료 | 확인 내용과 적용 |
|---|---|
| [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) | 이름·설명을 먼저 보고 선택 후 본문을 읽음. 좁은 트리거, `.agents/skills`, `$` 명시 호출을 채택. |
| [OpenAI: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 실행 전 계층별 지침을 읽음. 저장소 유지관리 지침을 짧게 두고 설치 대상 프로젝트의 기존 지침은 덮어쓰지 않음. |
| [OpenAI: Skill evals](https://developers.openai.com/blog/eval-skills) | 명시·암시·문맥·negative control을 구분. 정적 검사와 실제 forward 평가를 별도 기록. 글의 과거 `.codex/skills` 예제를 최신 경로와 혼동하지 않음. |
| [OpenAI: Rethinking skills](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | 과도한 설명과 넓은 트리거를 줄이고 작은 라우터를 사용. 문서 참조이며 해당 모델 실행·연결 권고가 아님. |
| [OpenAI: Iterating workflows](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) | 워크플로를 반복 개선하는 예제. 예제의 파일 트리·스택을 모든 과제에 강제하지 않음. |
| [OpenAI: ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans) | 장시간 계획용 예제에서 관측 가능한 결과만 차용. 장문 계획 파일은 의무화하지 않음. |
| [OpenAI: Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) | 샌드박스와 승인·네트워크 통제를 존중. 설치 권한을 외부 전송 권한으로 해석하지 않음. |
| [OpenAI: Sandbox](https://learn.chatgpt.com/docs/sandboxing) | 도구가 실행한 명령도 환경 경계를 상속. 우회·권한 완화·업그레이드를 성능 기법으로 제안하지 않음. |
| [Agent Skills specification](https://agentskills.io/specification) | `SKILL.md`와 필수 name/description, 상대 참조를 사용. 별도 오케스트레이터 의존성 없음. |
| [Anthropic: Effective agents](https://www.anthropic.com/research/building-effective-agents) | 단순하고 조합 가능한 해법부터 시작. 추가 에이전트·프레임워크의 비용과 지연을 기본으로 부담하지 않음. 외부 모델 실행 지침이 아님. |
| [Anthropic: Context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) | 필요한 순간 파일을 선택해 읽는 접근. 공통 참조 전체를 매번 로드하지 않음. |
| [Anthropic: Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) | 메타데이터→본문→참조의 점진적 공개. 구현 코어 하나와 조건부 참조로 구성. |
| [Microsoft: Web architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures) | 단일 배포에서도 논리 경계를 둘 수 있음. 마이크로서비스나 .NET 도입을 강제하지 않음. |
| [JSON Schema: Objects](https://json-schema.org/understanding-json-schema/reference/object) | required와 속성 정의는 다르고 null은 부재와 다름. ID·0·문자열 변환·추가 필드 정책을 경계에서 확인. |
| [Microsoft: Normalization](https://learn.microsoft.com/en-us/previous-versions/troubleshoot/microsoft-365/microsoft-365-apps/access/database-normalization-description) | 중복과 불일치 의존성을 줄임. 변경되는 공급자 사실은 단일 원본과 ID 참조로 관리하되 정적 JSON에 DB를 강요하지 않음. |
| [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) | NULL·UNIQUE·참조 제약의 의미를 확인. 실제 DB 사용 시 그 버전을 기준으로 검증하며 양수 CHECK만으로 NOT NULL을 대체하지 않음. |
| [Playwright: Best practices](https://playwright.dev/docs/best-practices) | 관측 가능한 사용자 동작 검증의 근거. 자동조작 금지 환경에서는 실행하지 않고 수동 UI 점검과 허용 CLI 검사를 구분. |
| [OWASP: Input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | 형식과 업무 의미를 함께 검사. 검증을 권한 검사·SQL 파라미터화·출력 인코딩의 대체물로 취급하지 않음. |
| [SK hynix Talent Hub](https://talent.skhynix.com/hub/ko/company/story/237) | 공개 설명은 문제 정의·AI 활용·결과 검증의 과정과 결과를 강조. 작동 결과와 검증 증거를 함께 남기는 근거로만 사용. |
| [공개 행사 소개](https://skhynix-hackathon.com/ai-2026) | 현장 과제와 작동하는 결과물을 강조. 실제 문제·배점·개인 응시 시간·세부 허용 범위를 추론하지 않음. |
| [Cofa](https://verify.getcofa.com/en) | 산출물과 대화·도구 사용·검증 기록을 함께 본다는 공개 설명. 짧고 사실적인 의사결정 증거를 권장. |
| [Cofa Probe](https://verify.getcofa.com/en/probe) | 정해진 환경과 조건에서 과정·산출물을 다룸. 기록을 조작하거나 사후 답안을 생성하는 기능은 만들지 않음. |
| [Cofa 공개 작업환경 mock](https://www.getcofa.com/brochure-v2/workspace-mock.html) | 주문 재시도 중복·결제 실패 복구·API 계약 유지라는 공개 소개용 주제를 확인. 이를 바탕으로 별도 합성 starter를 작성했으며 실제 시험 문제·공식 starter로 주장하지 않음. 동시성·재시작은 자체 확장 검사. |

## 구조 선택과 한계

독립 조사·윤문·사소한 수정에는 코어가 선택되지 않도록 설명에 제외 조건을 둡니다. 본격 구현에서만 코어를 읽고, 인터뷰·조사·데이터·위험·고장·마감 문서는 해당 조건에만 읽습니다. 분할 스킬 여러 개와 비교한 자동 트리거 실험은 수행하지 않았으므로 이 구조가 더 우수하다고 주장하지 않습니다.

토큰 수와 지연의 감소는 목표이며 응답시간 실측이나 특정 제공 Codex 버전의 발견 성공을 보장하지 않습니다. 현재 공식 발견 경로와 제공 버전이 다르면 업그레이드 없이 목록 확인, 명시 호출, 필요한 본문 직접 읽기 순으로 확인합니다.
