  import {Map, Marker} from "pigeon-maps"

export default function AboutUs() {

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border rounded shadow text-center">
      <h1 className="text-2xl mb-2">About Us</h1>
      <p>Clinic Manager powered by FastAPI + React + Vite.</p>
  
      <Map height={600} defaultCenter={[45.1149, 4.086 ]} defaultZoom={14}>
        <Marker width={50} anchor={[45.1149, 4.086 ]}/>
      </Map>
    
    </div>
  );
}