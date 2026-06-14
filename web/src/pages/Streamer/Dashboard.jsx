import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../../components/Navbar';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const StreamerDashboard = () => {
  const [user, setUser] = useState(null);
  const [dailyChallenge, setDailyChallenge] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [aiIdeas, setAiIdeas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
    fetchDailyChallenge();
    fetchSubscription();
    fetchAiIdeas();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/profile/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setUser(response.data.user);
    } catch (error) {
      toast.error('Failed to fetch user data');
    }
  };

  const fetchDailyChallenge = async () => {
    try {
      const response = await axios.get(`${API_URL}/challenges/daily/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setDailyChallenge(response.data[0]);
    } catch (error) {
      toast.error('Failed to fetch daily challenge');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscription = async () => {
    try {
      const response = await axios.get(`${API_URL}/payments/subscription/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setSubscription(response.data);
    } catch (error) {
      console.log('No subscription yet');
    }
  };

  const fetchAiIdeas = async () => {
    try {
      const response = await axios.get(`${API_URL}/social/ai-ideas-list/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setAiIdeas(response.data.results || []);
    } catch (error) {
      console.log('Failed to fetch AI ideas');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar userName={user?.username} userRole="STREAMER" />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Total Points</h3>
            <p className="text-4xl font-bold text-blue-600">{user?.total_points || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Subscription</h3>
            <p className="text-xl font-bold text-green-600">{subscription?.plan?.name || '❌ None'}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Account Status</h3>
            <p className="text-xl font-bold text-purple-600">🎮 Active</p>
          </div>
        </div>

        {/* Daily Challenge */}
        {dailyChallenge && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-2xl font-bold mb-4">🎯 Today's Challenge</h2>
            <div className="border-l-4 border-blue-600 pl-4">
              <h3 className="text-xl font-bold">{dailyChallenge.challenge?.title}</h3>
              <p className="text-gray-600 my-2">{dailyChallenge.challenge?.description}</p>
              <div className="flex gap-4 mt-4">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-bold">
                  Difficulty: {dailyChallenge.challenge?.difficulty}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-bold">
                  Points: {dailyChallenge.challenge?.reward_points}
                </span>
              </div>
              <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-bold">
                Start Challenge
              </button>
            </div>
          </div>
        )}

        {/* AI Generated Ideas */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">🤖 AI Generated Ideas</h2>
          <p className="text-gray-600 mb-4">Best ideas for premium subscribers</p>
          {aiIdeas.length === 0 ? (
            <p className="text-gray-600">No AI ideas available yet</p>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {aiIdeas.map((idea) => (
                <div key={idea.id} className="border border-gray-200 p-4 rounded-lg hover:shadow-lg transition">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg flex-1">{idea.title}</h3>
                    <span className="text-2xl">{idea.is_premium_only ? '🔒' : '🔓'}</span>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{idea.description}</p>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-500">🎮 {idea.game_category}</span>
                    <span className="text-red-600">❤️ {idea.rating}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StreamerDashboard;
