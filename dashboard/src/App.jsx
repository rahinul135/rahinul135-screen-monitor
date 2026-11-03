import React, { useState } from 'react';
import { Shield, Monitor, Bot, Settings, RefreshCw, Clock, User, Power, Search, Send, Trash2, Plus, CheckCircle, XCircle } from 'lucide-react';

const API_URL = 'https://screen-monitor-cc1w.onrender.com';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [page, setPage] = useState('overview');

  if (!token) return <Login onLogin={setToken} />;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f3f4f6' }}>
      <aside style={{ width: 256, background: '#1e293b', color: 'white', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
          <Shield size={32} color="#60a5fa" />
          <span style={{ fontWeight: 'bold', fontSize: 18 }}>Monitor Admin</span>
        </div>
        <nav style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {[
            { id: 'overview', label: 'Overview', icon: <RefreshCw size={20} /> },
            { id: 'clients', label: 'Client PCs', icon: <Monitor size={20} /> },
            { id: 'bots', label: 'Bots & Groups', icon: <Bot size={20} /> },
            { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
          ].map(item => (
            <button key={item.id} onClick={() => setPage(item.id)}
              style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                background: page === item.id ? '#2563eb' : 'transparent', color: page === item.id ? 'white' : '#cbd5e1' }}>
              {item.icon}<span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div style={{ padding: 16, borderTop: '1px solid #334155' }}>
          <button onClick={() => { setToken(null); localStorage.removeItem('token'); }}
            style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', border: 'none', background: 'none', color: '#94a3b8', cursor: 'pointer', width: '100%' }}>
            <Power size={20} /><span>Logout</span>
          </button>
        </div>
      </aside>

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <header style={{ height: 64, background: 'white', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 32px' }}>
          <h1 style={{ fontSize: 20, fontWeight: 600, color: '#1f2937' }}>
            {page === 'overview' && 'Overview'}
            {page === 'clients' && 'Client PCs'}
            {page === 'bots' && 'Bots & Groups'}
            {page === 'settings' && 'Settings'}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 14, color: '#6b7280' }}>{new Date().toLocaleString()}</span>
            <div style={{ width: 40, height: 40, background: '#2563eb', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>A</div>
          </div>
        </header>

        <div style={{ padding: 32, overflow: 'auto' }}>
          {page === 'overview' && <OverviewPage />}
          {page === 'clients' && <ClientsPage />}
          {page === 'bots' && <BotsPage />}
          {page === 'settings' && <SettingsPage />}
        </div>
      </main>
    </div>
  );
}

function Login({ onLogin }) {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [err, setErr] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (user === 'admin' && pass === 'admin123') {
      onLogin('mock-token');
    } else {
      setErr('Invalid credentials. Try: admin / admin123');
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ background: 'white', borderRadius: 16, padding: 40, width: '100%', maxWidth: 400, boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ width: 80, height: 80, background: '#2563eb', borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
            <Shield size={40} color="white" />
          </div>
          <h2 style={{ fontSize: 24, fontWeight: 'bold', color: '#111827' }}>Admin Login</h2>
          <p style={{ color: '#6b7280' }}>Employee Screen Monitor</p>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <div>
            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 6 }}>Username</label>
            <div style={{ position: 'relative' }}>
              <User style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} size={20} />
              <input type="text" placeholder="Admin username" value={user} onChange={e => setUser(e.target.value)}
                style={{ width: '100%', paddingLeft: 44, paddingRight: 16, padding: 14, border: '2px solid #e5e7eb', borderRadius: 12, fontSize: 16, outline: 'none' }} />
            </div>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 6 }}>Password</label>
            <input type="password" placeholder="••••••••" value={pass} onChange={e => setPass(e.target.value)}
              style={{ width: '100%', padding: 14, border: '2px solid #e5e7eb', borderRadius: 12, fontSize: 16, outline: 'none' }} />
          </div>
          {err && <p style={{ color: '#dc2626', textAlign: 'center', fontSize: 14 }}>{err}</p>}
          <button type="submit" style={{ width: '100%', padding: 14, background: '#2563eb', color: 'white', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 'bold', cursor: 'pointer' }}>
            Secure Login
          </button>
        </form>
      </div>
    </div>
  );
}

function OverviewPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 24 }}>
        <StatCard label="Total Clients" value="47" sub="Registered PCs" color="#2563eb" icon={<Monitor />} />
        <StatCard label="Online Now" value="43" sub="Active pulse" color="#16a34a" icon={<CheckCircle />} />
        <StatCard label="Offline" value="4" sub="Last seen > 5m" color="#dc2626" icon={<XCircle />} />
      </div>
      <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Clock size={20} color="#2563eb" /> Recent Activity
        </h3>
        {[
          { pc: 'OFFICE-PC-01', msg: 'Screenshot sent to Group A', time: 'Just now' },
          { pc: 'SALES-LAPTOP', msg: 'Heartbeat received', time: '30s ago' },
          { pc: 'OFFICE-PC-05', msg: 'Config updated: Interval set to 2m', time: '5m ago' },
        ].map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '12px 0', borderBottom: i < 2 ? '1px solid #f3f4f6' : 'none' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#2563eb' }} />
            <div style={{ flex: 1 }}>
              <span style={{ fontWeight: 600 }}>{item.pc}</span>
              <span style={{ color: '#6b7280', margin: '0 8px' }}>—</span>
              <span style={{ color: '#374151' }}>{item.msg}</span>
            </div>
            <span style={{ color: '#9ca3af', fontSize: 12 }}>{item.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, color, icon }) {
  return (
    <div style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <p style={{ color: '#6b7280', fontSize: 14, marginBottom: 4 }}>{label}</p>
        <p style={{ fontSize: 32, fontWeight: 'bold', color }}>{value}</p>
        <p style={{ color: '#9ca3af', fontSize: 12 }}>{sub}</p>
      </div>
      <div style={{ width: 48, height: 48, background: '#f3f4f6', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
        {icon}
      </div>
    </div>
  );
}

function ClientsPage() {
  return (
    <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
      <div style={{ padding: 24, borderBottom: '1px solid #f3f4f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: 18, fontWeight: 600 }}>Connected PCs</h3>
        <div style={{ position: 'relative' }}>
          <Search style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} size={18} />
          <input type="text" placeholder="Search PC name or IP..." style={{ paddingLeft: 40, paddingRight: 16, padding: 8, border: '1px solid #e5e7eb', borderRadius: 8, outline: 'none' }} />
        </div>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#f9fafb' }}>
            {['Client PC', 'Status', 'Interval', 'Assigned Group', 'Last Seen', 'Actions'].map(h => (
              <th key={h} style={{ padding: '12px 24px', textAlign: 'left', fontSize: 12, fontWeight: 500, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[
            { name: 'OFFICE-PC-01', ip: '192.168.1.10', status: 'online', interval: '3m', group: 'Sales Team', last: '2m ago' },
            { name: 'SALES-LAPTOP', ip: '192.168.1.15', status: 'online', interval: '2m', group: 'Sales Team', last: '30s ago' },
            { name: 'RECEPTION-DESK', ip: '192.168.1.5', status: 'offline', interval: '5m', group: 'None', last: '4h ago' },
          ].map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
              <td style={{ padding: '16px 24px' }}><span style={{ fontWeight: 600 }}>{row.name}</span><br /><span style={{ fontSize: 12, color: '#9ca3af' }}>{row.ip}</span></td>
              <td style={{ padding: '16px 24px' }}><div style={{ display: 'flex', alignItems: 'center', gap: 8 }}><div style={{ width: 10, height: 10, borderRadius: '50%', background: row.status === 'online' ? '#22c55e' : '#9ca3af' }} /><span style={{ color: row.status === 'online' ? '#16a34a' : '#6b7280' }}>{row.status === 'online' ? 'Online' : 'Offline'}</span></div></td>
              <td style={{ padding: '16px 24px' }}>{row.interval}</td>
              <td style={{ padding: '16px 24px' }}>{row.group}</td>
              <td style={{ padding: '16px 24px', color: '#6b7280' }}>{row.last}</td>
              <td style={{ padding: '16px 24px', textAlign: 'right' }}><button style={{ color: '#2563eb', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Configure</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BotsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: 18, fontWeight: 600 }}>Telegram Bots & Groups</h3>
        <button style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
          <Plus size={18} /> Add New Bot
        </button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 24 }}>
        {[
          { name: 'Sales Team Monitoring', token: '123456:ABC...XYZ', group: '-100123456789', clients: 12 },
          { name: 'Admin Reports', token: '987654:DEF...QWE', group: '-100987654321', clients: 4 },
        ].map((bot, i) => (
          <div key={i} style={{ background: 'white', borderRadius: 12, padding: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h4 style={{ fontWeight: 600 }}>{bot.name}</h4>
              <span style={{ fontSize: 11, background: '#dcfce7', color: '#16a34a', padding: '4px 8px', borderRadius: 4, fontWeight: 600 }}>ACTIVE</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, color: '#6b7280' }}><Shield size={14} />{bot.token}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, color: '#6b7280' }}><Send size={14} />{bot.group}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, color: '#6b7280' }}><Monitor size={14} />{bot.clients} Clients assigned</div>
            </div>
            <div style={{ display: 'flex', gap: 8, paddingTop: 16, borderTop: '1px solid #f3f4f6' }}>
              <button style={{ flex: 1, padding: 8, background: '#f3f4f6', border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 600 }}>Edit Bot</button>
              <button style={{ padding: 8, background: '#fee2e2', border: 'none', borderRadius: 6, cursor: 'pointer', color: '#dc2626' }}><Trash2 size={16} /></button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div style={{ maxWidth: 640, background: 'white', borderRadius: 12, padding: 32, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>Global Settings</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
        <div>
          <label style={{ display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 6 }}>Default Interval (Minutes)</label>
          <input type="number" defaultValue={3} style={{ width: '100%', padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 16 }} />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: 14, fontWeight: 500, color: '#374151', marginBottom: 6 }}>Admin Password</label>
          <input type="password" placeholder="••••••••" style={{ width: '100%', padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 16 }} />
        </div>
        <button style={{ padding: '12px 24px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 8, fontSize: 16, fontWeight: 600, cursor: 'pointer' }}>Save Changes</button>
      </div>
      <div style={{ paddingTop: 24, borderTop: '1px solid #e5e7eb' }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Software Updates</h3>
        <div style={{ padding: 16, background: '#f9fafb', borderRadius: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <p style={{ fontWeight: 600 }}>Current Agent Version: v1.0.0</p>
            <p style={{ fontSize: 14, color: '#6b7280' }}>Released on 2026-11-01</p>
          </div>
          <button style={{ color: '#2563eb', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Upload New Agent</button>
        </div>
      </div>
    </div>
  );
}
