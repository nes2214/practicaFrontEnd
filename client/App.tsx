import useSWR from 'swr'

export default function App() {

  const fetcher = (url :string) => fetch(url).then(r => r.json())

  const { data, error } = useSWR("/api/time", fetcher)

  if (error)
    return <p className="text-center text-danger m-5 fs-4">{error}</p>

  if (data == undefined) {
    return <p></p>
  }

  return (
    <p className="text-center m-5 fs-3">The current time is {data.time}.</p>
  )
}
