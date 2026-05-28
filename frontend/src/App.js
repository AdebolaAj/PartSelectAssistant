import React from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";
import companyLogoIcon from "./img/ps-25-year-logo.svg"
import orderStatusLogo from './img/order_status_logo.png'
import userAccountLogo from './img/user_icon_header.png'

function App() {
  const [toggleAccountMenu, setToggleAccountMenu] = React.useState(false)

  return (
    <div className="App">
      <div className="heading">
        <span> 
        <a href="https://www.partselect.com/" target="_blank">
            <img src={companyLogoIcon} alt="partselect-icon" width="250" height="100" />
          </a>
        </span>
        <div className="contact-info">
          <div style={{fontSize: 18}}>1-855-987-0987</div>
          <div style={{fontSize: 12}}>Monday to Saturday</div>
          <div style={{fontSize: 12}}>8am - 9pm EST</div>
        </div>
        <div
          onClick={() => setToggleAccountMenu(!toggleAccountMenu)}
          role="button"
        >
          <img src={userAccountLogo} alt="user account logo" width="30" height="30"></img>
          <span>Your Account</span>
        </div>
      </div>
        <ChatWindow/>
    </div>
  );
}

export default App;
