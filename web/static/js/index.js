async function get_network_latlons() {
  return new Promise((resolve, reject) => {
    fetch("/get_network_latlons", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        resolve(data);
      })
      .catch((error) => reject(error));
  });
}

window.addEventListener('load', async () => {

  mapboxgl.accessToken = 'pk.eyJ1IjoidGxhcmtpbjgiLCJhIjoiY2xmeXN4dzVhMDVxZDNycGQ0eWx1bmF5OSJ9.M61_GmXbb9Cu1QissnrggQ';
  const map = new mapboxgl.Map({
    container: 'map', // container ID
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/streets-v12', // style URL
    center: [-111.521483, 40.632181], // starting position [lng, lat]
    zoom: 12 // starting zoom
  });

  map.on('load', () => {
    // map.addSource('utah-bike-network-data', {
    //   type: 'vector',
    //   url: 'mapbox://tlarkin8.utah-bike-network'
    // });

    // get_network_latlons().then((data) => {
    //   let node_latlngs = data['nodes']
    //   let edge_latlngs = data['edges']
    //   let i = 0
    //   for (let latlng of edge_latlngs) {
    //     let geojsonLine = {
    //       'type': 'geojson',
    //       'data': {
    //         'type': 'Feature',
    //         'properties': {},
    //         'geometry': {
    //           'type': 'LineString',
    //           'coordinates': latlng
    //         }
    //       }
    //     }
    //     map.addSource(`route${i}`, geojsonLine);
    //     map.addLayer({
    //       'id': `route${i}`,
    //       'type': 'line',
    //       'source': `route${i}`,
    //       'layout': {
    //         'line-join': 'round',
    //         'line-cap': 'round'
    //       },
    //       'paint': {
    //         'line-color': '#888',
    //         'line-width': 2
    //       }
    //     });
    //     i++
    //   }
    // })
  });

})


    // ###########  LEAFLET
    // let map = L.map("map").setView([40.632181, -111.521483], 15);

    // L.tileLayer(
    //   "https://api.mapbox.com/styles/v1/tlarkin8/clfyt0742000801oanabhunsf/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoidGxhcmtpbjgiLCJhIjoiY2xmeXN4dzVhMDVxZDNycGQ0eWx1bmF5OSJ9.M61_GmXbb9Cu1QissnrggQ",
    //   {
    //     maxZoom: 19,
    //     attribution:
    //       '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    //   }
    // ).addTo(map);
    // L.tileLayer(
    //   "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
    //   {
    //     maxZoom: 19,
    //     attribution:
    //       '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    //   }
    // ).addTo(map);

    // var bounds = [
    //   [40.651808, -111.529923],
    //   [40.631618, -111.507764],
    // ];
    // let rectangle = L.rectangle(bounds, { color: "#ff7800", weight: 1 }).addTo(
    //   map
    // );
    // map.fitBounds(bounds);
    // var locationFilter = new L.LocationFilter().addTo(map);


    // get_network_latlons().then((data) => {
    //   let node_latlngs = data['nodes']
    //   let edge_latlngs = data['edges']
    //   for (let latlng of edge_latlngs) {
    //     let polyLine = L.polyline(latlng, {color: 'blue', weight: 1.5}).addTo(map)
    //   }

    //   for (let latlng of node_latlngs) {
    //     L.circle([latlng[0], latlng[1]], {color: 'blue', radius: 3}).addTo(map);
    //   }
    // })
