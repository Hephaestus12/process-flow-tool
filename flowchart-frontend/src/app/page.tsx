// pages/index.tsx
import type { NextPage } from "next";
import Head from "next/head";
import FlowchartEditor from "../components/FlowchartEditor";

const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>Flowchart Maker</title>
        <meta name="description" content="A simple flowchart tool" />
      </Head>
      <main>
        <h1 style={{ textAlign: "center" }}>Flowchart Maker</h1>
        <FlowchartEditor />
      </main>
    </div>
  );
};

export default Home;
