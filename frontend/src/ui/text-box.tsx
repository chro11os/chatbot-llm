export default function TextBox() {
  return (
    // ponytail: field-sizing-content does the auto-grow (Chrome/Safari); Firefox keeps the min height and scrolls
    <textarea
      name="text"
      required
      placeholder="Message… (Enter to send, Shift+Enter for a new line)"
      onKeyDown={(e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault()
          e.currentTarget.form?.requestSubmit()
        }
      }}
      className="flex-1 field-sizing-content min-h-24 max-h-64 resize-none bg-gray-900 p-3 m-2 text-white text-sm border border-gray-700 disabled:opacity-50"
    />
  )
}
