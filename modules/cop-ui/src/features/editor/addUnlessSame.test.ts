import { describe, expect, it } from "vitest";
import { addUnlessSame } from "./addUnlessSame";
import { offsetPad } from "./offsetPad";

const key = (o: { north_m: number; east_m: number }) => `${o.north_m},${o.east_m}`;

describe("same spot twice in the route window (Part1-41)", () => {
  it("a click on the previous point's spot adds nothing; elsewhere it adds", () => {
    const a = { north_m: -10, east_m: -710 };
    expect(addUnlessSame([a], { north_m: -10, east_m: -710 }, key)).toEqual([a]);
    expect(addUnlessSame([a], { north_m: 520, east_m: -470 }, key)).toEqual([a, { north_m: 520, east_m: -470 }]);
    expect(addUnlessSame([], a, key)).toEqual([a]);
  });
  it("points on one spot share a label, so the first number is not hidden under the second", () => {
    const pad = offsetPad([{ north_m: -10, east_m: -710 }, { north_m: -10, east_m: -710 }, { north_m: 520, east_m: -470 }], 360);
    expect(pad.labels.map((l) => l.text)).toEqual(["1·2", "3"]);
    expect(pad.labels[0].at).toEqual(pad.toXY({ north_m: -10, east_m: -710 }));
  });
});
