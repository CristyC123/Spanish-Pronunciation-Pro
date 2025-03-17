import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js';
import { getAuth, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { getFirestore, doc, setDoc, getDocs } from 'https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBbYT2LDueQRIToeNPMGYP3DO9fpKPOGhU",
  authDomain: "spanish-pronunciation-pro.firebaseapp.com",
  projectId: "spanish-pronunciation-pro",
  storageBucket: "spanish-pronunciation-pro.firebasestorage.app",
  messagingSenderId: "894004914288",
  appId: "1:894004914288:web:eed0401f39f093c2576cb5"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);

const uploadData = async () => {
  const data = {
    key1: "testblurb",
    key2: 12345,
    key3: new Date(),
  };

  try {
    const document = doc(db, "reciepts", "rJswHKF8XnzbhBB1Bd5l");
    let dataUpdated = await setDoc(document, data);


  } catch (error) {
    console.log('error in uploading data')
  }
}

const getData = async () => {
  try {
    const collectionRef = collection(db, "reciepts");
    const finalData = [];
    const q = query(collectionRef);

    const docSnap = await getDocs();

    docSnap.forEach((doc) => {
      finalData.push(doc.data());
    });
    return finalData;
  } catch (error) {
    console.log('Error In Fetching Data');
  }
}

exports = {
  app,
  uploadData,
  getData
}

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