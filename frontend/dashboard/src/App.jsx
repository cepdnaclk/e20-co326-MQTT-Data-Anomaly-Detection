import { useState, useEffect} from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import {io} from "socket.io-client";

// create a socket to receive real time data
const socket = io("http://localhost:5000");


function App(){

  const[data, setData] = useState({});
   
  useEffect(()=>{
    socket.on("sensor-data",(msg)=>{
        console.log("Live data: ", msg);
        setData(msg);
    });

    return () => socket.off("sensor-data");
  }, []);

  return (
    <div style={{ textAlign: "center" }}>
      <h1>IoT Dashboard</h1>
      <h2>Temperature: {data.temperature ?? "--"} °C</h2>
      <h2>Humidity: {data.humidity ?? "--"} %</h2>
    </div>
  );
}

export default App;