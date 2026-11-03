import Button from '../ui/button'
import TextBox from '../ui/text-box'
export default function Chatbox({ onReply }: { onReply: (text: string) => void }) {
  async function send(formData: FormData) {
          const res = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: formData.get('text') }),
          })
          const data = await res.json()
          onReply(data.reply)
      }

    return (
        <div className="justify-center items-center flex">
            <form action={send}>
                <div className="items-center flex justify-center m-7">
                    <TextBox />
                </div>
                    <Button>Send</Button>
            </form>
        </div>
    )
}
