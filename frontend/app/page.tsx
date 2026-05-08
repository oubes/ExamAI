"use client";

import { useEffect, useState } from "react";

export default function Home() {

  const [data, setData] = useState<any>(null);

  useEffect(() => {

    fetch("http://127.0.0.1:8000/api/v1/health")
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setData(data);
      })
      .catch((err) => {
        console.error(err);
      });

  }, []);

  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold">
        ExamAI Frontend
      </h1>

      <pre className="mt-5">
        {JSON.stringify(data, null, 2)}
      </pre>
    </main>
  );
}