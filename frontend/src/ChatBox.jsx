import React, { useState } from 'react';

function ChatBox({ onClose }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const handleSend = async () => {
        if (!input.trim()) {
            return
        }

        setMessages([...messages, { text: input, sender: 'user' }]);
        const userMessage = input;
        setInput('');

        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });
            
            const data = await response.json();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: 'ai', text: data.response || 'No response from AI' },
            ]);
        }
        catch (error) {
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: 'ai', text: 'Error communicating with server' },
            ]);
        }
    };

    return (
        <div className="fixed bottom-0 right-0 m-4 w-80 h-96 bg-white border border-gray-300 rounded-lg shadow-lg flex flex-col">
            <div className="flex justify-between items-center p-2 border-b border-gray-300">
                <h2 className="text-lg font-bold">Chat with AI</h2>
                <button onClick={onClose} className="text-red-500 font-bold">X</button>
            </div>
            <div className="flex-1 p-2 overflow-y-auto">
                {messages.map((msg, index) => (
                    <div key={index} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                        <span className={`inline-block p-2 rounded ${msg.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'}`}>
                            {msg.text}
                        </span>
                    </div>
                ))}
            </div>
            <div className="p-2 border-t border-gray-300">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded"
                    placeholder="Type your message..."
                />
                <button onClick={handleSend} className="mt-2 w-full bg-blue-500 text-white p-2 rounded">Send</button>
            </div>
        </div>
    );
}

export default ChatBox;