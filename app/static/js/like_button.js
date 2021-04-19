"use strict";

const e = React.createElement;
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

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    if (this.state.liked) {
      return "You liked this.";
    }

    return e(
      "button",
      { onClick: () => this.setState({ liked: true }) },
      "Like"
    );
  }
}

const domContainer = document.querySelector("#like_button_container");
ReactDOM.render(e(LikeButton), domContainer);
