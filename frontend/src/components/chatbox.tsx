export default function Chatbox () {
    function send(formData: FormData) {
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: formData.get('text') }),
        })
    }

    return (
        <div className="justify-center items-center hover: bg-amber-300 m-7 flex">
            <form action={send}>
                <div className="items-center flex justify-center m-7">
                    <input name="text" />
                </div>
                <div className="items-center flex justrify-center m-4">
                    <button>Send</button>
                </div>
            </form>
        </div>
    )
}