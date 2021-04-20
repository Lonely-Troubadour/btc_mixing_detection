import logo from "./logo.svg";
import "./App.css";
import React, { useState, useEffect } from "react";
import axios from "axios";
import Table from "./components/Table";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [dataPage, setDataPage] = useState(10);
  const [columns, setColumns] = useState(["Id", "Hash", "Height", "Time"]);
  const [pageList, setPageList] = useState(Array.from({length: 10}, (_, i) => i + 1))
  const tx_type = window.tx_type;
  var coinswap_data = [];

  const fetchData = async () => {
    const res = await axios.get("api/table/?page=" + currentPage + "&type=" + tx_type);
    if (tx_type == "CoinSwap") {
      let old_data = res.data;
      for (let i = 0; i < old_data.length; i++) {
        let id = old_data[i][0];
        let hash = "First: " + old_data[i][1] + "; Paired:" + old_data[i][2];
        let height = old_data[i][3];
        let time = old_data[i][4];
        // console.log([id, hash, height, time]);
        coinswap_data.push([id, hash, height, time]);
      }
      // console.log(coinswap_data);
      setData(coinswap_data);
    } else {
      setData(res.data);
    }
    // console.log(columns);
    // console.log(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [loading]);

  if (data == "0") {
    return (
      <h1 class="ui center aligned icon header">
        <i class="ambulance icon"></i>Oops!
        <div class="sub header">There is no data.</div>
      </h1>
    );
  }

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber["number"]);
    if (pageNumber["number"] > 4) {
      setPageList(Array.from({length: 10}, (_, index) => (index + pageNumber["number"] - 4 )))
    }
    setLoading(true)
  }

  return (
    <div className="App">
      {/* <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p> */}
      {/* <p>{data}</p> */}
      {/* <p>My token = {window.token}</p> */}
      {/* <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header> */}
      <Table columns={columns} data={data} pageList={pageList} paginate={paginate} />
    </div>
  );
}

export default App;
