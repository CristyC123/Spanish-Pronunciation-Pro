import React from 'react';
import api from './api.js';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button"; // Import Shadcn Button
import Layout from './components/layout.jsx';  // Import Layout component
import { Toaster } from '@/components/ui/sonner'; // Import Toaster component for notifications

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
import ProfilePage from './pages/profilePage.jsx'; // Import ProfilePage component
import SettingsPage from './pages/settingsPage.jsx'; // Import SettingsPage component
import { useAuthState } from 'react-firebase-hooks/auth';

import { ProfileProvider } from './profileContext.jsx';
import { useProfile } from './profileContext.jsx';

import { queryClient } from './queryClient.jsx';
import { QueryClientProvider } from '@tanstack/react-query'
import { useQuery } from '@tanstack/react-query';
import { fetchData } from './fetchData.js';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

import { MoonLoader } from 'react-spinners';

const localStoragePersister = createSyncStoragePersister ({
  storage: window.localStorage,
});

persistQueryClient({
  queryClient,
  persister: localStoragePersister,
  maxAge: 1000 * 60 * 60 * 24,
});

function AppContent() {
  const [ user ] = useAuthState(auth);
  const [isFetching, setIsFetching] = useState(true);
  const [fetchingData, setFetchingData] = useState(true);
  const { setProfile, profile } = useProfile();
  
    const { data, isLoading } = useQuery({
    queryFn: () => fetchData(user.uid),
    queryKey: ["profile", user?.uid],
    enabled: !!user?.uid,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
    staleTime: 1000 * 60 * 60 * 24,
    retry: false,
  });

  useEffect(() => {
    if(data) {
      setProfile(data, user.uid)
    }
  } ,[data, user])
  

// Uses firebase auth state change method to update the user.
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setIsFetching(false)
        return;
      }
      setIsFetching(false);
    })

    return () => unsubscribe();
  }, [])

  
  // Fetches user data immediately as soon as user is found.
  /*
  useEffect(() => {
    const getUser = async () => {
      if (user) {
        try {
          let response = await api.get(`/getUser?uid=${user.uid}`)
          console.log(response)
        } catch (error) {
          console.log(error.response.status)
          if(error.response.status === 400) {
            await api.post('/setUser', {id: user.uid}).catch(() => {})
            await api.post('/setUserStatistics', {id: user.uid}).catch(() => {})
            await api.post('/setAchievements', {id: user.uid}).catch(() => {})
            await api.post('/setLessonProgress', {id: user.uid}).catch(() => {})
            console.log("Account initialized.")
          }
        }

        try {
          let fetchedData = await api.get(`/getUserStatistics?uid=${user.uid}`)
          let userStats = fetchedData.data.user_stats
          setProfile(prev => ({
              ...prev,
            lessonsCompleted: userStats.completed_lessons ?? prev.lessonsCompleted,
            accuracyRate: userStats.accuracy_rate ?? prev.accuracyRate,
            practiceSessions: userStats.practice_sessions ?? prev.practiceSessions,
            studyStreak: userStats.study_streak ?? prev.studyStreak}));
          fetchedData = await api.get(`/getAchievements?uid=${user.uid}`)
          let fetchedAchievements = fetchedData.data.achievements.achievements
          setProfile(prev => ({
            ...prev,
            achievements: fetchedAchievements
          }))

        } catch (error) {
          console.log(error)
        }

        try {
          const fetchedData = await api.get(`/getActivityHistory?uid=${user.uid}`)

          setProfile(prev => ({
            ...prev,
            activities: fetchedData.data.activity_history
          }))

        } catch (error) {
          console.log(error)
        }

        try {
          const fetchedData = await api.get(`/getLessonProgress?uid=${user.uid}`)
          setProfile(prev => ({
            ...prev,
            lessons: fetchedData.data.lesson_data
          }))

          setFetchingData(false)
        } catch(error) {
          console.log(error)
        }
     }
  }
  if(user) getUser();

}, [user])
*/

  // If user is being fetched don't load page.
  if(isFetching || isLoading ) {
    return <div className="flex justify-center items-center min-h-screen">
      <MoonLoader size={50} color="#08b4fc"/>
      </div>
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
        
          <Route element={<Layout user={user}/>}>
            <Route path="/lessonsPractice" element={<LessonsPracticePage/>} />
            <Route path="/lessons" element={<LessonsPage user={user} isFetching={fetchingData}/>} />
            <Route path="/profile" element={<ProfilePage user={user} />} />
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            <Route path="/settings" element={<SettingsPage user={user}/>} />
          </Route>
        </Route>
      </Routes>
      <Toaster richColors position="bottom-right" />
      
    </div>
  );
}
export default function App() {
  return (
    <QueryClientProvider client={queryClient} >
      <ProfileProvider>
        <AppContent/>
      </ProfileProvider>
    </QueryClientProvider>
  )
};