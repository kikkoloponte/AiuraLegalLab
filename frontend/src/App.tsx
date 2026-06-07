import { Routes, Route } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { Dashboard } from '@/pages/Dashboard'
import { Chat } from '@/pages/Chat'
import { Documents } from '@/pages/Documents'
import { Wiki } from '@/pages/Wiki'
import { History } from '@/pages/History'
import { Graph } from '@/pages/Graph'
import { Settings } from '@/pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="chat" element={<Chat />} />
        <Route path="documents" element={<Documents />} />
        <Route path="wiki" element={<Wiki />} />
        <Route path="history" element={<History />} />
        <Route path="graph" element={<Graph />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
