import Markdown from 'react-markdown'

export default function ReplyScreen({ reply }: { reply: string }) {
    return (
        <div className="prose m-7">
            <Markdown>{reply}</Markdown>
        </div>
    )
}
