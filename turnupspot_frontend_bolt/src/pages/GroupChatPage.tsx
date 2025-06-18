import React, { useState, useRef, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Send, Paperclip, Image as ImageIcon, Smile, MoreVertical } from 'lucide-react';

interface Message {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
  isCurrentUser: boolean;
}

const GroupChatPage = () => {
  const { id } = useParams<{ id: string }>();
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      senderId: '1',
      senderName: 'Bright',
      content: 'Hey everyone! Ready for today\'s game?',
      timestamp: '10:30 AM',
      isCurrentUser: false,
    },
    {
      id: '2',
      senderId: '2',
      senderName: 'Gbolahan',
      content: 'Yes, I\'ll be there at 6!',
      timestamp: '10:32 AM',
      isCurrentUser: false,
    },
    {
      id: '3',
      senderId: '3',
      senderName: 'Deji',
      content: 'Don\'t forget to bring the new balls',
      timestamp: '10:35 AM',
      isCurrentUser: true,
    },
    {
      id: '4',
      senderId: '4',
      senderName: 'Kojay',
      content: 'I\'ll bring extra water for everyone',
      timestamp: '10:40 AM',
      isCurrentUser: false,
    },
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      senderId: '3', // Current user ID
      senderName: 'Deji', // Current user name
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isCurrentUser: true,
    };

    setMessages([...messages, newMessage]);
    setMessage('');
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to={`/sports/groups/${id}`} className="text-gray-600 hover:text-gray-900">
            <ArrowLeft size={24} />
          </Link>
          <div>
            <h1 className="text-xl font-semibold">Weekend Warriors FC</h1>
            <p className="text-sm text-gray-500">24 members</p>
          </div>
        </div>
        <button className="text-gray-600 hover:text-gray-900">
          <MoreVertical size={24} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.isCurrentUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                msg.isCurrentUser
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-900'
              }`}
            >
              {!msg.isCurrentUser && (
                <p className="text-sm font-medium text-indigo-600 mb-1">{msg.senderName}</p>
              )}
              <p className="text-sm">{msg.content}</p>
              <p className={`text-xs mt-1 ${msg.isCurrentUser ? 'text-indigo-200' : 'text-gray-500'}`}>
                {msg.timestamp}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
          >
            <Paperclip size={20} />
          </button>
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
          >
            <ImageIcon size={20} />
          </button>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700 rounded-full hover:bg-gray-100"
          >
            <Smile size={20} />
          </button>
          <button
            type="submit"
            className="p-2 text-white bg-indigo-600 rounded-full hover:bg-indigo-700"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default GroupChatPage;