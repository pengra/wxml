import React, { Component } from 'react';
import Jumbotron from 'react-bootstrap/lib/Jumbotron';
import Button from 'react-bootstrap/lib/Button';
import Documentation from './Documentation'
import Dashboard from './Dashboard'
import './App.css';

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      rakanReady: true
    }
  }
  render() {
    if (!this.state.rakanReady) {
      // some documentation + instructions
      return (
        <div className="container">
          <Jumbotron>
            <h1>Xayah</h1>
            <p>
              Xayah works in conjunction with Rakan. Check the Rakan documentation to get Rakan to communicate to Xayah.
              By default, Xayah is configured to listen to port <code>3000</code>.
            </p>
            <br/>
            <Button variant="primary" onClick={() => this.setState({rakanReady: true})}>Rakan is Ready</Button>
          </Jumbotron>
          <Documentation />
        </div>
      );
    } else {
      // launch the dashboard
      return (
        <Dashboard rakanPort={3001} />
      );
    }
  }
}

export default App;
