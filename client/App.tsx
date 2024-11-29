import { useEffect, useState } from "react";

export default function App() {

  const [currentTime, setCurrentTime] = useState(0)
  const [log,setLog] = useState("")

  useEffect(() => {

    const fetchTime = async () => {

      
      const response = await fetch('/api/time')
      if (response.status != 200) {
        setLog(response.statusText)
        return
      }

      const data = await response.json()
      setCurrentTime(data.time)
      
    }

    fetchTime()

  }, [])

  return (
    <div className="container">
      <p className="text-center m-5 p-5 fs-3">The current time is {currentTime}.</p>
      <p className="text-center text-danger fs-4">{log}</p>
    </div>
  )
}

