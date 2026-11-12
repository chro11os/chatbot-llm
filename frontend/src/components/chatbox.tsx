import { useFormStatus } from 'react-dom'
import Button from '../ui/button'
import TextBox from '../ui/text-box'
import UsageRing, { type Usage } from './usagering'

// useFormStatus only works in a component rendered *inside* the <form>
function Fields({ usage }: { usage: Usage[] }) {
    const { pending } = useFormStatus()
    return (
        <fieldset disabled={pending} className="flex items-end w-full">
            <TextBox />
            <div className="flex flex-col items-center">
                <UsageRing usage={usage} />
                <Button>{pending ? 'Sending…' : 'Send'}</Button>
            </div>
        </fieldset>
    )
}

export default function Chatbox({ onSend, usage }: { onSend: (text: string) => Promise<void>; usage: Usage[] }) {
    return (
        <form action={(formData) => onSend(formData.get('text') as string)} className="p-2">
            <Fields usage={usage} />
        </form>
    )
}
