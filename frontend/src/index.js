import { initializeApp } from "firebase/app";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import { getFirestore, doc, setDoc, getDocs, collection, query } from "firebase/firestore";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: "spanish-pronunciation-pro.firebaseapp.com",
  projectId: "spanish-pronunciation-pro",
  storageBucket: "spanish-pronunciation-pro.firebasestorage.app",
  messagingSenderId: "894004914288",
  appId: "1:894004914288:web:eed0401f39f093c2576cb5"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export const uploadData = async () => {
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
};

export const getData = async () => {
  try {
    const collectionRef = collection(db, "reciepts");
    const finalData = [];
    const q = query(collectionRef);

    const docSnap = await getDocs(q);

    docSnap.forEach((docItem) => {
      finalData.push(docItem.data());
    });
    return finalData;
  } catch (error) {
    console.log('Error In Fetching Data', error);
  }
};

export { app };

// onAuthStateChanged(auth, user => {
//   if(user != null) 
//   {
//     console.log('logged in!');
//   }
//   else 
//   {
//     console.log('no user');
//   }

// });