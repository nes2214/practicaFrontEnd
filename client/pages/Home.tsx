
import useSWR from 'swr'
import xtecLogo from '../assets/xtec.svg'

function Time() {
  const fetcher = (arg: any, ...args: any) =>
    fetch(arg, ...args).then((res) => res.json());

  const { data, error, isValidating } = useSWR("/api/time", fetcher, {
    refreshInterval: 1000, // actualitza cada segon
  });

  if (error)
    return (
      <p className="text-center text-danger m-5 text-4xl">
        Error fetching time: {error.message || error.toString()}
      </p>
    );

  if (isValidating)
    return <p className="text-center text-warning m-5 fs-4">Loading ...</p>;

  return (
    <p className="text-center mt-5 text-xl">
      The current time is {data?.time}.
    </p>
  );
}

export default function Home() {

  return <div>
    <p className="">
      <a href="https://xtec.dev" target="_blank">
        <img src={xtecLogo} width="10%" height="10%" className="text-center rounded h-12 object-contain" alt="xtec.dev Logo" />
      </a>
    </p>
    <Time />
  </div>
}
