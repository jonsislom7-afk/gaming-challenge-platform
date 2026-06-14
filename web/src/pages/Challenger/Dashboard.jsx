import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../../components/Navbar';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const ChallengerDashboard = () => {
  const [user, setUser] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    game_category: '',
    difficulty: 'MEDIUM',
    reward_points: 100,
  });

  useEffect(() => {
    fetchUserData();
    fetchChallenges();
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

  const fetchChallenges = async () => {
    try {
      const response = await axios.get(`${API_URL}/challenges/daily/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setChallenges(response.data);
    } catch (error) {
      toast.error('Failed to fetch challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChallenge = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/challenges/create/`, formData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      toast.success('Challenge created successfully!');
      setFormData({ title: '', description: '', game_category: '', difficulty: 'MEDIUM', reward_points: 100 });
      setShowCreateForm(false);
      fetchChallenges();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create challenge');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar userName={user?.username} userRole="CHALLENGER" />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Total Points</h3>
            <p className="text-4xl font-bold text-blue-600">{user?.total_points || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Challenges Created</h3>
            <p className="text-4xl font-bold text-green-600">{challenges.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-600 text-sm font-bold">Account Status</h3>
            <p className="text-xl font-bold text-purple-600">🎯 Active</p>
          </div>
        </div>

        {/* Create Challenge Button */}
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-bold mb-8"
        >
          + Create New Challenge
        </button>

        {/* Create Challenge Form */}
        {showCreateForm && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-2xl font-bold mb-4">Create Challenge</h2>
            <form onSubmit={handleCreateChallenge} className="space-y-4">
              <input
                type="text"
                placeholder="Challenge Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              <textarea
                placeholder="Challenge Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="4"
                required
              />
              <div className="grid grid-cols-2 gap-4">
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="EASY">Easy</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HARD">Hard</option>
                  <option value="EXPERT">Expert</option>
                </select>
                <input
                  type="number"
                  placeholder="Reward Points"
                  value={formData.reward_points}
                  onChange={(e) => setFormData({ ...formData, reward_points: parseInt(e.target.value) })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-bold"
                >
                  Create Challenge
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg font-bold"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Challenges List */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">Your Challenges</h2>
          {challenges.length === 0 ? (
            <p className="text-gray-600">No challenges created yet</p>
          ) : (
            <div className="space-y-4">
              {challenges.map((challenge) => (
                <div key={challenge.id} className="border border-gray-200 p-4 rounded-lg">
                  <h3 className="text-xl font-bold">{challenge.challenge?.title}</h3>
                  <p className="text-gray-600 mb-2">{challenge.challenge?.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-blue-600">Points: {challenge.challenge?.reward_points}</span>
                    <span className="text-sm font-bold text-green-600">Difficulty: {challenge.challenge?.difficulty}</span>
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

export default ChallengerDashboard;
