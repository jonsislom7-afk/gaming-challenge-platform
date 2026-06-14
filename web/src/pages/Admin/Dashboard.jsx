import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '../../components/Navbar';
import toast from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const AdminDashboard = () => {
  const [user, setUser] = useState(null);
  const [pendingPayments, setPendingPayments] = useState([]);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPayment, setSelectedPayment] = useState(null);

  useEffect(() => {
    fetchUserData();
    fetchPendingPayments();
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

  const fetchPendingPayments = async () => {
    try {
      const response = await axios.get(`${API_URL}/payments/admin/pending/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      setPendingPayments(response.data);
    } catch (error) {
      toast.error('Failed to fetch pending payments');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPayment = async (paymentId, isVerified) => {
    try {
      await axios.post(
        `${API_URL}/payments/admin/verify/${paymentId}/`,
        { is_verified: isVerified },
        { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } }
      );
      toast.success(isVerified ? 'Payment verified!' : 'Payment rejected!');
      setSelectedPayment(null);
      fetchPendingPayments();
    } catch (error) {
      toast.error('Failed to verify payment');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar userName={user?.username} userRole="ADMIN" />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Admin Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow border-t-4 border-red-600">
            <h3 className="text-gray-600 text-sm font-bold">Pending Payments</h3>
            <p className="text-4xl font-bold text-red-600">{pendingPayments.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-t-4 border-yellow-600">
            <h3 className="text-gray-600 text-sm font-bold">CHECK Verification</h3>
            <p className="text-4xl font-bold text-yellow-600">👁️</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-t-4 border-green-600">
            <h3 className="text-gray-600 text-sm font-bold">System Status</h3>
            <p className="text-xl font-bold text-green-600">✅ All Good</p>
          </div>
        </div>

        {/* Pending Payments */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">💳 Pending Payments (CHECK Verification)</h2>
          {pendingPayments.length === 0 ? (
            <p className="text-gray-600">No pending payments</p>
          ) : (
            <div className="space-y-4">
              {pendingPayments.map((payment) => (
                <div key={payment.id} className="border border-yellow-300 bg-yellow-50 p-4 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-bold">Payment ID: {payment.id}</p>
                      <p className="text-gray-600">Amount: {payment.amount} {payment.currency}</p>
                      <p className="text-gray-600">Method: {payment.payment_method}</p>
                      <p className="text-gray-600">CHECK #: {payment.check_number}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleVerifyPayment(payment.id, true)}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold"
                      >
                        ✓ Verify
                      </button>
                      <button
                        onClick={() => handleVerifyPayment(payment.id, false)}
                        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-bold"
                      >
                        ✗ Reject
                      </button>
                    </div>
                  </div>
                  {payment.check_image && (
                    <div className="mt-4">
                      <p className="text-sm font-bold mb-2">CHECK Image:</p>
                      <img src={payment.check_image} alt="Check" className="max-w-xs rounded" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
