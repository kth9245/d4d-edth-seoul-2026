# ontology — 기체 종류 is-a 계층에서 능력을 추론한다(결정 0038)

- 책임: `Scenario.ontology`(종류 계층·행동 묶음)를 따라 기체가 어떤 행동을 왜 할 수 있거나 없는지 판정한다. 닫힌 세계: 계층 어디에도 없으면 못 함.
- 입력: `Ontology`, `Scenario` / 출력: `CapabilityReason`, `list[ActionKind]`, `Scenario`(기체 채움), `OntologyView`
- 공개 API(`__init__.py`): kind_chain, explain_capability, infer_capabilities, fill_vehicle_kinds, ontology_view
- 새 동작은 `/new-action`(= `uv run python scripts/new_action.py ontology <verb_noun> "<설명>"`)으로 시작한다.
- 담당: 리드 kth9245. 작업은 자기 worktree에서 main으로(결정 0010·0014).
