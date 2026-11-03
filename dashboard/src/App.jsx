import React, { useState, useEffect } from 'react';
import { Shield, Monitor, Bot, Settings as SettingsIcon, RefreshCw, Clock, User, Power, Search, Send, Trash2, Plus, CheckCircle, XCircle } from 'lucide-react';

const API_URL = 'https://screen-monitor-cc1w.onrender.com';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [page, setPage] = useState('overview');
  const [clients, setClients] = useState([]);
  const [bots, setBots] = useState([]);
  const [settings, setSettings] = useState({});

  useEffect(() => {
    if (token) fetchAll();
  }, [token]);

  const fetchAll = async () => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [cRes, bRes, sRes] = await Promise.all([
        fetch(`${API_URL}/admin/clients`, { headers }),
        fetch(`${API_URL}/admin/bots`, { headers }),
        fetch(`${API_URL}/admin/settings`, { headers })
      ]);
      setClients((await cRes.json()).clients || []);
      setBots((await bRes.json()).bots || []);
      setSettings(await sRes.json());
    } catch (e) { console.error('Fetch error:', e); }
  };

  if (!token) return <Login onLogin={(t) => { setToken(t); localStorage.setItem('token', t); }} />;

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <aside className="w-64 bg-slate-800 text-white flex flex-col">
        <div className="p-6 text-xl font-bold border-b border-slate-700">Monitor Admin</div>
        <nav className="flex-1 p-4 space-y-2">
          {['overview', 'clients', 'bots', 'settings'].map(p => (
            <button key={p} onClick={() => setPage(p)} className={`w-full text-left p-3 rounded-lg capitalize ${page === p ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
              {p}
            </button>
          ))}
        </nav>
        <button onClick={() => { localStorage.removeItem('token'); setToken(null); }} className="p-4 text-slate-400 hover:text-white">Logout</button>
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6 capitalize">{page}</h2>
        {page === 'overview' && <Overview clients={clients} />}
        {page === 'clients' && <Clients clients={clients} token={token} />}
        {page === 'bots' && <Bots bots={bots} token={token} />}
        {page === 'settings' && <SettingsView settings={settings} token={token} />}
      </main>
    </div>
  );
}

function Login({ onLogin }) {
  const handleSubmit = async (e) => {
    e.preventDefault();
    const user = e.target.user.value;
    const pass = e.target.pass.value;
    const r = await fetch(`${API_URL}/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass })
    });
    const d = await r.json();
    if (d.access_token) onLogin(d.access_token);
    else alert('Invalid credentials');
  };
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-lg w-96">
        <h2 className="text-xl font-bold mb-6 text-center">Admin Login</h2>
        <input name="user" placeholder="Username" className="w-full p-2 border rounded mb-4" required />
        <input name="pass" type="password" placeholder="Password" className="w-full p-2 border rounded mb-6" required />
        <button className="w-full bg-blue-600 text-white p-2 rounded">Login</button>
      </form>
    </div>
  );
}

function Overview({ clients }) {
  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-lg shadow"><h3>Total</h3><p className="text-3xl font-bold">{clients.length}</p></div>
      <div className="bg-white p-6 rounded-lg shadow"><h3>Online</h3><p className="text-3xl font-bold text-green-600">{clients.filter(c=>c.is_active).length}</p></div>
      <div className="bg-white p-6 rounded-lg shadow"><h3>Offline</h3><p className="text-3xl font-bold text-red-600">{clients.filter(c=>!c.is_active).length}</p></div>
    </div>
  );
}

function Clients({ clients, token }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <table className="w-full">
        <thead><tr className="border-b"><th>Name</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {clients.map(c => (
            <tr key={c.id} className="border-b">
              <td className="p-3">{c.pc_name}</td>
              <td className="p-3">{c.is_active ? '✅ Online' : '❌ Offline'}</td>
              <td className="p-3"><button className="text-blue-600">Configure</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Bots({ bots, token }) {
  return (
    <div className="grid grid-cols-2 gap-6">
      {bots.map(b => (
        <div key={b.id} className="bg-white p-6 rounded-lg shadow">
          <p className="font-bold">{b.name}</p>
          <p className="text-sm text-gray-500">{b.token}</p>
        </div>
      ))}
    </div>
  );
}

function SettingsView({ settings, token }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow max-w-lg">
      <h3 className="font-bold mb-4">Settings</h3>
      <input defaultValue={settings.default_interval} className="w-full p-2 border rounded mb-4" />
      <button className="bg-blue-600 text-white px-4 py-2 rounded">Save</button>
    </div>
  );
}
