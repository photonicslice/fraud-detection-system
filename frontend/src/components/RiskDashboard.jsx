import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { AlertCircle, MapPin, Store, TrendingUp } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

const Input = ({ label, name, type = "text", value, onChange, placeholder, required = false }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {label} {required && <span className="text-red-500">*</span>}
    </label>
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

const TransactionForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    card_id: '',
    merchant_id: '',
    amount: '',
    location_id: '',
    device_id: '',
    ip_address: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
      location_id: formData.location_id ? parseInt(formData.location_id) : null
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Verify New Transaction</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Card ID"
            name="card_id"
            value={formData.card_id}
            onChange={handleChange}
            placeholder="Enter card ID"
            required
          />
          <Input
            label="Merchant ID"
            name="merchant_id"
            value={formData.merchant_id}
            onChange={handleChange}
            placeholder="Enter merchant ID"
            required
          />
          <Input
            label="Amount"
            name="amount"
            type="number"
            value={formData.amount}
            onChange={handleChange}
            placeholder="Enter amount"
            required
          />
          <Input
            label="Location ID"
            name="location_id"
            type="number"
            value={formData.location_id}
            onChange={handleChange}
            placeholder="Enter location ID (optional)"
          />
          <Input
            label="Device ID"
            name="device_id"
            value={formData.device_id}
            onChange={handleChange}
            placeholder="Enter device ID (optional)"
          />
          <Input
            label="IP Address"
            name="ip_address"
            value={formData.ip_address}
            onChange={handleChange}
            placeholder="Enter IP address (optional)"
          />
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-2 px-4 rounded-md text-white font-medium 
              ${isLoading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {isLoading ? 'Verifying...' : 'Verify Transaction'}
          </button>
        </form>
      </CardContent>
    </Card>
  );
};

const RiskScore = ({ score, label, icon: Icon }) => (
  <Card className="bg-white">
    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
      <CardTitle className="text-sm font-medium text-gray-500">{label}</CardTitle>
      <Icon className="w-4 h-4 text-gray-500" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">
        {Math.round(score)}
        <span className="text-sm font-normal text-gray-500 ml-1">/ 100</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
        <div 
          className={`h-2.5 rounded-full ${
            score >= 75 ? 'bg-red-500' : 
            score >= 50 ? 'bg-yellow-500' : 
            'bg-green-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
    </CardContent>
  </Card>
);

const TransactionDetails = ({ transaction }) => {
  if (!transaction) return null;

  const riskLevelColor = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Card ID</p>
            <p className="font-medium">{transaction.card_id}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Amount</p>
            <p className="font-medium">${transaction.amount.toFixed(2)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Merchant ID</p>
            <p className="font-medium">{transaction.merchant_id}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Location ID</p>
            <p className="font-medium">{transaction.location_id || 'N/A'}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Timestamp</p>
            <p className="font-medium">{formatDate(transaction.timestamp)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Risk Level</p>
            <span className={`px-2 py-1 rounded-full text-xs ${riskLevelColor[transaction.risk_level.toLowerCase()]}`}>
              {transaction.risk_level}
            </span>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Fraud Probability</p>
            <p className="font-medium">{(transaction.fraud_probability * 100).toFixed(1)}%</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-gray-500">Status</p>
            <p className="font-medium">{transaction.status}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const RiskDashboard = () => {
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const verifyTransaction = async (transactionData) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/v1/transactions/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to verify transaction');
      }

      const data = await response.json();
      setTransaction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Risk Assessment Dashboard</h1>
          <p className="mt-2 text-gray-600">Real-time transaction risk analysis</p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <TransactionForm onSubmit={verifyTransaction} isLoading={loading} />

        {transaction && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <RiskScore 
                score={transaction.fraud_probability * 100} 
                label="Fraud Probability" 
                icon={AlertCircle}
              />
              <RiskScore 
                score={transaction.pattern_risk_score * 100} 
                label="Pattern Risk" 
                icon={TrendingUp}
              />
              <RiskScore 
                score={transaction.location_risk_score * 100} 
                label="Location Risk" 
                icon={MapPin}
              />
              <RiskScore 
                score={transaction.merchant_risk_score * 100} 
                label="Merchant Risk" 
                icon={Store}
              />
            </div>

            <TransactionDetails transaction={transaction} />
          </>
        )}
      </div>
    </div>
  );
};

export default RiskDashboard;