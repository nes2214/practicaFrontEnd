import { useEffect, useState } from "react";

export default function App() {

  const [currentTime, setCurrentTime] = useState(0)

  useEffect(() => {

    const fetchTime = async () => {

      
      const response = await fetch('/api/time')

      const data = await response.text()

      //const data = await response.json()
      console.log(data)
      //setCurrentTime(data.time)
      
    }

    fetchTime()

  }, [])

  return (
    <div className="container">
      <p>The current time is {currentTime}.</p>
    </div>
  )
}

