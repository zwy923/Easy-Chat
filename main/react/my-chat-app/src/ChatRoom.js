import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ChatRoom({ roomName, username }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await axios.get(`http://localhost:5001/get_room_messages`, {
          params: { room_name: roomName },
        });
        setMessages(response.data); // Assuming the backend returns an array of messages
      } catch (error) {
        console.error('Error fetching messages:', error);
      }
    };

    fetchMessages();
    // Set an interval to poll for new messages every 5 seconds
    const interval = setInterval(fetchMessages, 5000);

    return () => clearInterval(interval); // Clear the interval when the component unmounts
  }, [roomName]);

  const sendMessage = async () => {
    if (!newMessage.trim()) return; // Prevent sending empty messages

    try {
      const response = await axios.post('http://localhost:5001/send_to_room', {
        room_name: roomName,
        username,
        text: newMessage,
      });
      if (response.status === 200) {
        setNewMessage('');
        await fetchMessages(); // Refresh messages after sending a new one
      }
    } catch (error) {
      console.error('Send message error:', error);
    }
  };

  // Helper function to fetch messages
  const fetchMessages = async () => {
    try {
      const response = await axios.get(`http://localhost:5001/get_room_messages`, {
        params: { room_name: roomName },
      });
      setMessages(response.data); // Update the messages state with the new messages
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  return (
    <div>
      <h2>Room: {roomName}</h2>
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className="message">
            <span className="username">{message.username}: </span>
            <span className="text">{message.text}</span>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default ChatRoom;
