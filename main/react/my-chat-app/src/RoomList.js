import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RoomList({ onRoomSelect, username }) {
  const [rooms, setRooms] = useState([]);
  const [newRoomName, setNewRoomName] = useState('');

  useEffect(() => {
    // Fetch rooms or listen for new rooms
  }, []);

  const handleJoinRoom = (roomName) => {
    onRoomSelect(roomName);
  };

  const handleCreateRoom = async () => {
    try {
      const response = await axios.post('http://localhost:5001/create_room', { room_name: newRoomName, username });
      if (response.status === 201) {
        onRoomSelect(newRoomName);
      }
    } catch (error) {
      console.error('Create room error:', error);
    }
  };

  return (
    <div>
      {rooms.map((room) => (
        <button key={room} onClick={() => handleJoinRoom(room)}>
          {room}
        </button>
      ))}
      <input value={newRoomName} onChange={(e) => setNewRoomName(e.target.value)} placeholder="New Room Name" />
      <button onClick={handleCreateRoom}>Create Room</button>
    </div>
  );
}

export default RoomList;
