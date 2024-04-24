import React, { useState } from 'react';
import Login from './Login';
import RoomList from './RoomList';
import ChatRoom from './ChatRoom';

function App() {
  const [username, setUsername] = useState('');
  const [roomName, setRoomName] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (user) => {
    setUsername(user);
    setIsLoggedIn(true);
  };

  const handleRoomSelection = (room) => {
    setRoomName(room);
  };

  return (
    <div>
      {!isLoggedIn ? (
        <Login onLogin={handleLogin} />
      ) : (
        <>
          <RoomList onRoomSelect={handleRoomSelection} username={username} />
          {roomName && <ChatRoom roomName={roomName} username={username} />}
        </>
      )}
    </div>
  );
}

export default App;
