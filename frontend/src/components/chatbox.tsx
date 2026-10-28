export default function chatbox () {
    function send(formData: FormData) {
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: formData.get('text') }),
        })
    }

    return (
        <form action={send}>
            <input name="text" />
            <button>Send</button>
        </form>
    )
}