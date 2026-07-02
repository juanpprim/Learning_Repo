import { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [status, setStatus] = useState("loading"); // loading | error | ready

  useEffect(() => {
    fetch(`${API_URL}/items`)
      .then((res) => res.json())
      .then((data) => {
        setItems(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    // TODO: POST to /items and append the created item to state
  }

  if (status === "loading") return <p>Loading...</p>;
  if (status === "error") return <p>Failed to load items.</p>;

  return (
    <main>
      <h1>Items</h1>
      <ul>
        {items.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
      <form onSubmit={handleSubmit}>
        <input value={name} onChange={(e) => setName(e.target.value)} />
        <button type="submit">Add</button>
      </form>
    </main>
  );
}
