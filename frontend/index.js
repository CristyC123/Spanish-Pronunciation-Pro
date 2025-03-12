import { initializeApp } from "firebase/app";
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBbYT2LDueQRIToeNPMGYP3DO9fpKPOGhU",
  authDomain: "spanish-pronunciation-pro.firebaseapp.com",
  projectId: "spanish-pronunciation-pro",
  storageBucket: "spanish-pronunciation-pro.firebasestorage.app",
  messagingSenderId: "894004914288",
  appId: "1:894004914288:web:eed0401f39f093c2576cb5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);

onAuthStateChanged(auth, user => {

if(user != null) 
{
  console.log('logged in!');
}
else 
{
  console.log('no user');
}

})