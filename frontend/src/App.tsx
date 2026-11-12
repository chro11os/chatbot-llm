import { startTransition, useEffect, useOptimistic, useState } from 'react';
import Chatbox from "./components/chatbox";
import ReplyScreen from "./components/replyscreen";
import type { Usage } from "./components/usagering";
import Pet from "./components/pet";

type Msg = { role: string; text: string }
type Turn = { text: string; status: number; ms: number; body: unknown }

function Messages({ items }: { items: Msg[] }) {
    return items.map((m, i) => (
        <div key={i} className="border-b border-gray-800">
            <div className="text-xs font-bold uppercase text-gray-500 mx-7 mt-3">{m.role}</div>
            <ReplyScreen reply={m.text} />
        </div>
    ))
}

// Drag bar between columns. Pointer capture keeps the drag going even when the
// mouse moves faster than the 4px bar; movementX is how far it moved since the last event.
function Handle({ onDrag }: { onDrag: (dx: number) => void }) {
    return (
        <div
            className="w-1 shrink-0 cursor-col-resize touch-none bg-gray-800 hover:bg-gray-600"
            onPointerDown={e => { e.preventDefault(); e.currentTarget.setPointerCapture(e.pointerId) }}
            onPointerMove={e => { if (e.currentTarget.hasPointerCapture(e.pointerId)) onDrag(e.movementX) }}
        />
    )
}

// ponytail: side columns 200px–half the window; widths reset on reload (localStorage if that annoys)
const clamp = (w: number) => Math.min(Math.max(w, 200), window.innerWidth / 2)

export default function App() {
    const [left, setLeft] = useState(() => window.innerWidth / 3)
    const [right, setRight] = useState(() => window.innerWidth / 3)
    const [history, setHistory] = useState<Msg[]>([])
    const [messages, setMessages] = useState<Msg[]>([])
    const [turns, setTurns] = useState<Turn[]>([])

    function loadHistory() {
        fetch('/api/history').then(r => r.json()).then(setHistory).catch(() => setHistory([]))
    }
    useEffect(loadHistory, [])

    // usage from each successful turn (empty until the backend returns it)
    const usage = turns.flatMap(t => (t.body as { usage?: Usage } | null)?.usage ?? [])

    // shown = messages + temporary entries that disappear when the form action finishes
    const [shown, addShown] = useOptimistic(messages, (s, m: Msg) => [...s, m])

    // while a request runs, shown has the 2 temporary entries messages doesn't
    const thinking = shown.length > messages.length

    async function send(text: string) {
        addShown({ role: 'user', text })
        addShown({ role: 'model', text: '_thinking…_' })
        const start = performance.now()
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        })
        const body = await res.json().catch(() => null)
        // updates after an await must be wrapped to stay part of the action
        startTransition(() => {
            setTurns(t => [...t, { text, status: res.status, ms: Math.round(performance.now() - start), body }])
            setMessages(m => [...m, { role: 'user', text }, {
                role: 'model',
                text: res.ok ? body.reply : `**Error ${res.status}:** ${body?.detail ?? 'no detail'}`,
            }])
        })
        loadHistory()
    }

    return (
        <div className="flex h-screen">
            <Pet thinking={thinking} />
            <section style={{ width: left }} className="shrink-0 overflow-y-auto">
                <h2 className="font-bold m-4">History ({history.length})</h2>
                <Messages items={history} />
            </section>
            <Handle onDrag={dx => setLeft(w => clamp(w + dx))} />
            <section className="flex-1 min-w-0 flex flex-col h-screen">
                <h2 className="font-bold m-4">Chat</h2>
                <div className="flex-1 overflow-y-auto"><Messages items={shown} /></div>
                <Chatbox onSend={send} usage={usage} />
            </section>
            <Handle onDrag={dx => setRight(w => clamp(w - dx))} />
            <section style={{ width: right }} className="shrink-0 overflow-y-auto">
                <h2 className="font-bold m-4">Debug</h2>
                {turns.map((t, i) => (
                    <pre key={i} className={`text-xs m-4 p-2 whitespace-pre-wrap ${t.status < 400 ? 'bg-gray-900' : 'bg-red-950'}`}>
                        {`POST /api/chat  ${t.status}  ${t.ms}ms\n> ${t.text}\n< ${JSON.stringify(t.body, null, 2)}`}
                    </pre>
                ))}
            </section>
        </div>
    );
}
