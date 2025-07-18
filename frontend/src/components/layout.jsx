import React from 'react';
import { Outlet } from 'react-router-dom'; 
import Navbar from './navbar.jsx'; 

function Layout({user}) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar user={user}/>
      <main className="flex-grow container mx-auto p-4 md:p-6"> 
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;