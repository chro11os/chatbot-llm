// Pixel art as text: each character is one pixel, '.' is empty.
const SPRITE = [
    '.....S.....',
    '.....O.....',
    '...OOOOO...',
    '..OOOOOOO..',
    '.OOEOOOEOO.',
    '.OOOOOOOOO.',
    '.OOOOOOOOO.',
    '..OOOOOOO..',
    '...O...O...',
]
const COLORS: Record<string, string> = { O: '#d97757', E: '#111827', S: '#fcd34d' }

export default function Pet({ thinking }: { thinking: boolean }) {
    return (
        <div className="fixed bottom-4 right-4 pointer-events-none flex flex-col items-center">
            {thinking && <div className="text-xs bg-gray-800 border border-gray-700 rounded px-2 mb-1">thinking…</div>}
            <svg viewBox="0 0 11 9" shapeRendering="crispEdges" aria-hidden="true"
                className={`w-11 pet-bob ${thinking ? 'pet-fast' : ''}`}>
                {SPRITE.flatMap((row, y) => [...row].map((c, x) => c !== '.' && (
                    <rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill={COLORS[c]}
                        className={c === 'E' ? 'pet-eye' : undefined} />
                )))}
            </svg>
        </div>
    )
}
