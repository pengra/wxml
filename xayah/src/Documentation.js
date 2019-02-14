import React, { Component } from 'react';
import Card from 'react-bootstrap/lib/Card';
import './App.css';

class Documentation extends Component {
  render() {
    return (
      <div className="container">
        <div className="row">
        <div className="col-md-4">
        <Card>
            <Card.Img variant="top" src="xayah.png" />
            <Card.Body>
                <Card.Title>Step 0: Start Xayah</Card.Title>
                <Card.Text>
                You got Xayah working.
                </Card.Text>
            </Card.Body>
        </Card>
        </div>
        <div className="col-md-4">
        <Card>
            <Card.Img variant="top" src="rakan.png" />
            <Card.Body>
                <Card.Title>Step 1: Start Rakan</Card.Title>
                <Card.Text>
                Check the Rakan documentation to get Rakan to do a walk.
                </Card.Text>
            </Card.Body>
        </Card>
        </div>
        </div>
      </div>
    );
  }
}

export default Documentation;
