import { useState } from "react";

// Top of the editor sidebar, above "＋ Role 새로 만들기" (decision 0053): a name and a purpose make an empty
// operation on the running one's map; it becomes the running one and the editor opens its overview.
export function NewOperationMenu({ onCreate }: { onCreate: (name: string, purpose: string) => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [purpose, setPurpose] = useState("");
  const close = () => {
    setOpen(false);
    setName("");
    setPurpose("");
  };
  return (
    <section className="newrole newop">
      <button className={open ? "newrole-toggle on" : "newrole-toggle"} aria-expanded={open}
        onClick={() => (open ? close() : setOpen(true))}>
        {open ? "× 닫기" : "＋ 작전 새로 만들기"}
      </button>
      {open && (
        <div className="newrole-manual">
          <input aria-label="작전 이름" placeholder="작전 이름" value={name} onChange={(e) => setName(e.target.value)} />
          <input aria-label="작전 목적" placeholder="목적 (선택)" value={purpose} onChange={(e) => setPurpose(e.target.value)} />
          <button className="make" disabled={!name.trim()} onClick={() => {
            onCreate(name.trim(), purpose.trim());
            close();
          }}>만들기</button>
        </div>
      )}
    </section>
  );
}
