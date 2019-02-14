import React, { Component } from 'react';
import { Map, TileLayer, Polygon, Tooltip, Circle, Polyline } from 'react-leaflet';
import Navbar from 'react-bootstrap/lib/Navbar';
import Nav from 'react-bootstrap/lib/Nav';
import './App.css';

class Precinct extends Component {
  // props:
    // name: name of precinct
    // color: color of precinct
    // map: map to render to
    // vertexes: vertex coordinates of polygon
    // parent: the precintmap instance
  render() {
    return (
      <div>
        <Polygon color={this.props.color} positions={this.props.vertexes}>
          <Tooltip direction="bottom" opacity={1}>{this.props.name}</Tooltip>
          {this.props.parent.state.showNodes ? <Circle center={this.props.nodeCoord} opacity={100} fillcolor={this.props.color} radius={2} /> : null}
        </Polygon>
      </div>
    );
  }
}

const colors = [
  "#001f3f", // Navy
  "#3D9970", // Olive
  "#FF851B", // Orange
  "#85144b", // Maroon
  "#DDDDDD", // Silver
  "#0074D9", // Blue
  "#2ECC40", // Green
  "#FF4136", // Red
  "#F012BE", // Fuchsia
  "#111111", // Black
  "#7FDBFF", // Aqua
  "#FFDC00", // Yellow
  "#B10DC9", // Purple
  "#39CCCC", // Teal
  "#AAAAAA", // Gray
  "#01FF70", // Lime
]

class PrecinctMap extends Component {
  // properties:
    // rakanPort: 3001
  constructor(props) {
    super(props)
    this.state = {
      showConnectivity: false, // show the connectivity (lines + nodes)
      showPolygons: true, // show the precinct polygons
      showNodes: false,
      edges: [], // node connection lines
      precincts: [], // precinct vertexes
      districts: [], // districts, where the index corresponds to an rid and the value is the district.
      nodeCoords: [], // the center of the polygon via vertex averages. Not accurate but it'll do for now.
      polygons: [], // the entire list of polygon objects constructed from precincts/districts
      polylines: [], // the entire list of edges to be rendered
      lat: 38.8796042, // camera settings default to United States overview
      lng: -95.8315692,
      zoom: 4,
      rakanWebsocket: null, // the rakan websocket
      iterations: 0, // number of iterations rakan has gone through so far
      screenBounds: {_northEast: {lat: 90, lng: 1000}, _southWest: {lat: -90, lng: -1000}}, // The boundaries of the map, blank on construction
    }

    this.connectRakan = this.connectRakan.bind(this);
    this.buildPolygons = this.buildPolygons.bind(this);
    this.buildPolylines = this.buildPolylines.bind(this);
  }
  
  // Loading Rakan
  connectRakan() {
    const rakanSocket = new WebSocket('ws://127.0.0.1:' + this.props.rakanPort);
    // store socket in state. Might be used later?
    this.setState({
      rakanWebsocket: rakanSocket
    })

    // on message, (rakan sent an update) update the map
    rakanSocket.onmessage = (event) => {
      // read payload
      let payload = JSON.parse(event.data);
      // update precincts, districts and iterations SHOULD they exist in the payload.
      if (payload.precinct_vertexes) {
        this.setState({
          precincts: payload['precinct_vertexes'],
        }, this.buildPolygons) // buildPolygon callback
      }
      if (payload.edges) {
        // some spoogati code just to get this working
        // edges = [(1,2), (3,4)] means 1 and 2 are connected, 3 and 4 are connected
        this.setState({
          edges: payload.edges.map((e) => {
            let x_total1 = 0
            let y_total1 = 0
            let x_total2 = 0
            let y_total2 = 0
            this.state.precincts[e[0]].map((item) => {
              x_total1 += item[0];
              y_total1 += item[1];
            })
            this.state.precincts[e[1]].map((item) => {
              x_total2 += item[0];
              y_total2 += item[1];
            })
            return [
              [y_total2 / this.state.precincts[e[1]].length, x_total2 / this.state.precincts[e[1]].length],
              [y_total1 / this.state.precincts[e[0]].length, x_total1 / this.state.precincts[e[0]].length],
            ];
          }),
        }, this.buildPolylines) // buildPolylines callback
      }
      if (payload.precinct_districts) {
        this.setState({
          districts: payload['precinct_districts'],
        }, this.buildPolygons)
      }
      if (payload.iterations) {
        this.setState({
          iterations: payload['iterations']
        })
      }
      if (payload.update && payload.update.length > 0) {
        let districts = this.state.districts
        payload['update'].map(e => {
          // e is a pair where the first element is an rid
          // second item is the new district number
          districts[e[0]] = e[1];
        })
        this.setState({
          districts: districts
        })
      }

      // close the socket
      // rakanSocket.close()
    }

  }

  componentDidMount() {
    // Create an event
    this.refs.map.leafletElement.on("moveend", () => {
      this.setState({
        screenBounds: this.refs.map.leafletElement.getBounds(),
      }, this.buildPolygons)
    })

    this.connectRakan();
  }

  buildPolygons() {
    // build the polygons & mark their centers
    if (this.state.precincts.length > 0 && this.state.districts.length > 0) {
      this.setState({
        nodeCoords: this.state.precincts.map((vertexes) => {
          let x_total = 0
          let y_total = 0
          vertexes.map((item) => {
            x_total += item[0];
            y_total += item[1];

          })
          return [x_total / vertexes.length, y_total / vertexes.length];
        }),
        polygons: this.state.precincts.map((e, i) => <Precinct 
          key={i} 
          name={i} 
          color={colors[this.state.districts[i]]} 
          vertexes={e.map((a) => [a[1], a[0]])}
          showNode={this.state.showNodes}
          showPolygons={this.state.showPolygons}
          parent={this}
        />)
      })
    }
  }

  buildPolylines() {
    this.setState({
      polylines: this.state.edges.map((e, i) => <Polyline
        key={i} 
        strokeWidth={0.01}
        color={"lime"}
        positions={e}
      />)
    })
  }

  render() {
    const position = [this.state.lat, this.state.lng]

    const north = this.state.screenBounds._northEast.lng;
    const east = this.state.screenBounds._northEast.lat;
    const south = this.state.screenBounds._southWest.lng;
    const west = this.state.screenBounds._southWest.lat;

    return (
      <Map center={position} zoom={this.state.zoom} id="mapid" style={{height: "90vh"}} ref='map'>
        <TileLayer attribution="Shout out to the amazing folks @ <a href='https://openstreetmap.org'>OpenStreetMap</a>" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>
        {this.state.polygons.map((e, i) => (
          this.state.nodeCoords[i][1] >= west && 
          this.state.nodeCoords[i][1] <= east && 
          this.state.nodeCoords[i][0] >= south && 
          this.state.nodeCoords[i][0] <= north
        ) ? e : null)}
        {this.state.showConnectivity ? this.state.polylineRenderList : null}
      </Map>
    );
  }
}

class Dashboard extends Component {
  // properties:
    // rakanPort: 3001
  constructor(props) {
    super(props)
    this.state = {
      currentPage: 0,
      steps: 0,
    }
  }
  render() {
    return (
      <div>
      <Navbar bg="dark" variant="dark">
        <Navbar.Brand>
          <img className="d-inline-block align-top" src="xayah.png" alt="" height="30" width="30"/>
          {' Project Xayah'}
        </Navbar.Brand>
        <Nav className="mr-auto">
          <Nav.Link active={this.state.currentPage === 0}>Visualization</Nav.Link>
          <Nav.Link active={this.state.currentPage === 1}>Rakan Statistics</Nav.Link>
          <Nav.Link active={this.state.currentPage === 2}>Other States</Nav.Link>
        </Nav>
        <Nav>
          <Nav.Link disabled={this.state.steps === 0}>Export {this.state.steps} Steps</Nav.Link>
        </Nav>
      </Navbar>
      <PrecinctMap rakanPort={this.props.rakanPort} />
      </div>
    );
  }
}

export default Dashboard;
