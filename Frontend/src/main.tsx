import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Welcome } from '../app/welcome/welcome';
import { Header } from '../app/header/header';
import 'bootstrap/dist/css/bootstrap.min.css';
import './app.css';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <main className="p-4 container mx-auto">
      {children}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Header />
    <Layout>
      <Routes>
        <Route path="/" element={<Welcome />} />
      </Routes>
    </Layout>
  </BrowserRouter>
);