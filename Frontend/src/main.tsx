import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from '../app/header/header';
import Container from 'react-bootstrap/Container';
import 'bootstrap/dist/css/bootstrap.min.css';
import './app.css';
import Gallery from '../app/gallery/gallery';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Container as="main" className="p-4 container mx-auto">
      {children}
    </Container>
  );
}

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <Header />
    <Layout>
      <Routes>
        <Route path="/" element={<Gallery />} />
      </Routes>
    </Layout>
  </BrowserRouter>
);