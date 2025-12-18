import { BrowserRouter, Routes, Route } from "react-router"
import useSWR from 'swr'
import xtecLogo from './assets/xtec.svg'
import Doctors from "./Doctors";

export default function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path={"/"} element={<Home />} />
        <Route path="/doctors" element={<Doctors />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>)
}


function Home() {

  return <div>
    <p className="">
      <a href="https://xtec.dev" target="_blank">
        <img src={xtecLogo} className="h-12 object-contain" alt="xtec.dev Logo" />
      </a>
    </p>
    <Time />
  </div>
}

function Time() {

  const fetcher = (arg: any, ...args: any) => fetch(arg, ...args).then((res) => res.json());

  const { data, error, isValidating } = useSWR("/api/time", fetcher)

  if (error)
    return <p className="text-center text-danger m-5 text-4xl">SSSS{error}</p>

  if (isValidating)
    return <p className="text-center text-warning m-5 fs-4">Loading ...</p>

  return (
    <p className="text-center mt-5 text-xl">The current time is {data.time}.</p>
  )
}

function NotFound() {
  return (
    <>
      <p className="text-danger fs-4">404 Not Found</p>
    </>
  )
}
