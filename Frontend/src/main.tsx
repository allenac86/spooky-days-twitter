import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Welcome } from '../app/welcome/welcome';
import './app.css';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <main className="pt-16 p-4 container mx-auto">
      {children}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Layout>
      <Routes>
        <Route path="/" element={<Welcome />} />
      </Routes>
    </Layout>
  </BrowserRouter>
);