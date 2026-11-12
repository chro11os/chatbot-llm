// Field names match Gemini's `usage` object (see memory/lastresponse.json)
export type Usage = {
    total_tokens: number
    total_input_tokens: number
    total_output_tokens: number
    total_thought_tokens: number
}

// ponytail: arbitrary session budget so the ring has something to fill toward, not a Gemini limit
const BUDGET = 100_000
const C = 2 * Math.PI * 16 // circumference of the r=16 circle

export default function UsageRing({ usage }: { usage: Usage[] }) {
    const sum = (k: keyof Usage) => usage.reduce((n, u) => n + (u[k] ?? 0), 0)
    const total = sum('total_tokens')
    const pct = Math.min(total / BUDGET, 1)

    return (
        <div className="relative group m-2">
            <svg viewBox="0 0 40 40" className="w-9 h-9 -rotate-90">
                <circle cx="20" cy="20" r="16" fill="none" stroke="#374151" strokeWidth="4" />
                <circle cx="20" cy="20" r="16" fill="none" stroke="#f3f4f6" strokeWidth="4"
                    strokeDasharray={C} strokeDashoffset={C * (1 - pct)} />
            </svg>
            <div className="absolute bottom-full right-0 mb-2 z-10 hidden group-hover:block whitespace-pre bg-gray-800 border border-gray-700 text-white text-xs p-2">
                {`Session: ${total.toLocaleString()} / ${BUDGET.toLocaleString()} tokens (${Math.round(pct * 100)}%)
Input: ${sum('total_input_tokens')}   Output: ${sum('total_output_tokens')}   Thought: ${sum('total_thought_tokens')}
Last turn: ${usage.at(-1)?.total_tokens ?? 0}   Turns: ${usage.length}`}
            </div>
        </div>
    )
}
