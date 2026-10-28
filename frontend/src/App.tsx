import { useState } from 'react';
import Chatbox from "./components/chatbox";
import ReplyScreen from "./components/replyscreen";
export default function App() {
    const [reply, setReply] = useState('')
    return(
        <>
            <ReplyScreen reply={reply}/>
            <Chatbox onReply={setReply}/>
        </>
    );
}        