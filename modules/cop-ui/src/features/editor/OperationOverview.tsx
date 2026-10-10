import type { Operation, VehicleSpec } from "../../contracts.gen";
import { OperationPanel } from "./OperationPanel";
import { StepCard } from "./StepCard";
import type { Column } from "./vehicleColumns";

type Props = {
  op: Operation;
  vehicles: VehicleSpec[];
  columns: Column[];
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
};

export function OperationOverview({ op, vehicles, columns, playName, onOpen }: Props) {
  return (
    <section className="overview">
      <OperationPanel op={op} vehicles={vehicles} playName={playName} onOpen={onOpen} />
      <div className="columns">
        {columns.map((col) => (
          <div key={col.vehicle_id} className="column">
            <div className="column-head">
              {col.vehicle_id}
              {col.reserve_for.length > 0 && <small> 예비: {col.reserve_for.join(", ")} 대신</small>}
            </div>
            {col.plays.map((cp) => (
              <div key={cp.play_id}>
                {cp.via && <div className="via">↓ '{cp.via}' 선택 시</div>}
                {cp.play ? (
                  <>
                    <button className="link play-title" onClick={() => onOpen(cp.play_id)}>
                      {cp.play.name}
                    </button>
                    {cp.play.steps.map((s) => (
                      <StepCard key={s.id} step={s} play={cp.play!} playName={playName} onOpen={onOpen} />
                    ))}
                  </>
                ) : (
                  <div className="step-card missing">없는 플레이: {cp.play_id}</div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}
