

function Chat() {
    return (
        <div className="chat-page">
            <h3>Bearcat Brain</h3>
            <textarea 
                rows="2" 
                className="form-control" 
                placeholder="Ask me C++ questions..."
            ></textarea>
            <button className="send-btn">
                Send
            </button>
        </div>
    );
}

export default Chat;