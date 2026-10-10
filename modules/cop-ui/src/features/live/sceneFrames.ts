import op from "../../../../../contracts/examples/operation.json";
import type { Frame, Operation, Polygon } from "../../contracts.gen";

// Dev only (?scene=s1..s6): the six 3-minute-script scenes from contracts/examples, shown without the gateway.
// App loads this module only under import.meta.env.DEV, so the demo build does not contain it.
const files = import.meta.glob<Frame>("../../../../../contracts/examples/frames/*.json", { eager: true, import: "default" });

export const SCENES: Record<string, Frame> = Object.fromEntries(
  Object.entries(files).map(([path, frame]) => [path.split("/").pop()!.split("_")[0], frame]),
);
export const SCENE_ZONE: Polygon = (op as Operation).zone;
