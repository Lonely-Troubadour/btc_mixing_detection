// const {useState, useEffect} = React;

const App = (props) => {
  const [data, setData] = React.useState([]);

  React.useEffect(() => {
    (async () => {
      const result = await axios({
        method: "get",
        url: "api/table/?id=1&type=fe",
        responseType: "json",
      });
      setData(result.data);
    })();
  }, []);
  console.log(data)

  return (
    <div>{data}</div>
  )
}

const domContainer = document.querySelector("#like_button_container");
ReactDOM.render(<App />, domContainer);
