import useSWR from 'swr'

export default function App() {

  const fetcher = (arg: any, ...args: any) => fetch(arg, ...args).then((res) => res.json());

  const { data, error, isValidating } = useSWR("/api/time", fetcher)

  if (error)
    return <p className="text-center text-danger m-5 fs-4">{error}</p>

  if (isValidating)
    return <p className="text-center text-warning m-5 fs-4">Loading ...</p>

  return (
    <p className="text-center m-5 fs-3">The current time is {data.time}.</p>
  )
}
