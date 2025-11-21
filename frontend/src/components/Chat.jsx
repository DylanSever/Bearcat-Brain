import { useRef } from 'react'
import { useState } from 'react'

function Chat() {
    const [input, setInput] = useState('');
    const [output, setOutput] = useState('');

    const inputRef = useRef(null);

    function handleSend() {
        if (input.trim() === '') return;
        setOutput(function(prev) {
            if (!prev) return input;
            return prev + '\n' + input;
        });
        setInput('');
        inputRef.current?.focus();
    }

    return (
        <div className="chat-page">
            <h3>Bearcat Brain</h3>

            <textarea
                className="chat-output"
                rows="20"
                readOnly={true}

                value={output}
            ></textarea>

            <textarea 
                className="form-control" 
                rows="2" 
                placeholder="Ask me C++ questions..."

                ref={inputRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
            ></textarea>

            <button className="send-btn" onClick={handleSend}>Send</button>
        </div>
    );
}

export default Chat;