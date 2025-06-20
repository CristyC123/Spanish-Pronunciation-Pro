import React from 'react';
import api from './api.js';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button"; // Import Shadcn Button
import Layout from './components/layout.jsx';  // Import Layout component

import LoginPage from './pages/loginPage.jsx'; // Import LoginPage component
import LessonsPracticePage from './pages/lessonsPracticePage.jsx'; // Import LessonsPage component
import Dashboard from './pages/dashboard.jsx'; // Import Dashboard component
import ForgotPasswordPage from './pages/passwordReset.jsx';  // Import ForgotPasswordPage component
import SignupPage from './pages/signup.jsx'; // Import SignupPage component
import LessonsPage from './pages/lessons.jsx'; // Import LessonsPage component

import { onAuthStateChanged} from 'firebase/auth';
import { useEffect, useState } from 'react';  
import { ProtectedRoute } from './components/protectedRoute.jsx';
import { auth } from './firebase.js';
import ProfilePage from './pages/profilePage.jsx';

function App() {
  const navigate = useNavigate('')
  const [user, setUser] = useState(null);
  const [isFetching, setIsFetching] = useState(true);
  const [profile, setProfile] = useState({
    name: "N/A",
    creationDate: "N/A"
  })

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser(user);
        setIsFetching(false)
        return;
      }

      setUser(null);
      setIsFetching(false);
    })

    return () => unsubscribe();
  }, [])

  // This is a mess, fix this later.
  useEffect(() => {
    const getUser = async () => {
      if (user) {
          setProfile(prev => ({
              ...prev,
            name: user.displayName ?? prev.name,
            creationDate: user.metadata.creationDate ?? prev.creationDate
      }));
     }
  }
  if(user) getUser();

}, [user])

  if(isFetching) {
    return <h2>Loading...</h2>
  }

  return (
    <div>
      {/* --- Route Display Area --- */}
      <Routes>
        {/* Routes without the navbar*/}
        <Route path="/" element={<LoginPage user={user} isFetching={isFetching}/>} />
        <Route path="/login" element={<LoginPage user={user} isFetching={isFetching} />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/passwordReset" element={<ForgotPasswordPage />} />

        <Route element={<ProtectedRoute user={user} />}>
        {/* Routes with the navbar, wrapped by the layout.jsx component.*/}
          <Route element={<Layout />}>
            <Route path="/lessonsPractice" element={<LessonsPracticePage user={user}/>} />
            <Route path="/lessons" element={<LessonsPage user={user}/>} />
            <Route path="/dashboard" element={<Dashboard user={user}/>} />
            <Route path="/profile" element={<ProfilePage user={user} profile={profile}/>} />
          </Route>
        </Route>

        {/* Routes with the navbar, wrapped by the layout.jsx component.*/}

        <Route path="/lessonsPractice" element={<LessonsPracticePage />} />

        <Route path="/lessons" element={<LessonsPage />} />

        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </div>
  );
}
export default App;