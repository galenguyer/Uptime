import logo from "./logo.svg";
import useSWR from "swr";
import "./App.css";
import Site from "./Site";

const path = "/api/v1/data";

function App() {
    const { data: data, error: error } = useSWR(path);
    if (error) {
        <div className="App">
            <h1>a fucky wucky happened, oopsie</h1>
        </div>;
    }
    if (!data) {
        <div className="App">
            <h1>loading</h1>
        </div>;
    }

    console.log(data);
    const dataList = [];
    for (const key in data) {
        dataList.push(data[key]);
    }

    return (
        <div className="App">
            {dataList.map((d) => (
                <Site data={d} />
            ))}
        </div>
    );
}

export default App;
