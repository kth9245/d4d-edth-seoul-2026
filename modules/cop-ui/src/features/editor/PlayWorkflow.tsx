import type { Play } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";
import type { Usage } from "./playUsage";
import { StepCard } from "./StepCard";

type Props = { play: Play; usage: Usage[]; playName: (id: string) => string | null; onOpen: (playId: string) => void };

export function PlayWorkflow({ play, usage, playName, onOpen }: Props) {
  return (
    <section className="workflow">
      <h2>
        {play.name} <small>{play.domains.map((d) => DOMAIN_LABEL[d]).join("·") || "영역 없음"}</small>
      </h2>
      <div className="usage">
        {usage.length === 0
          ? "이 작전에서 쓰는 기체 없음"
          : usage.map((u, i) => (
              <div key={i}>
                {u.vehicle_id} — {u.how}
              </div>
            ))}
      </div>
      {play.steps.map((s) => (
        <StepCard key={s.id} step={s} play={play} playName={playName} onOpen={onOpen} />
      ))}
    </section>
  );
}
