var network = null;
var currentID = 41;

function destroy() {
  if (network !== null) {
    network.destroy();
    network = null;
  }
}

function init() {
  $.getJSON('/connections', function(edges) {
    $.getJSON('/nodes', function(nodes) {
      destroy();

      // provide the data in the vis format
      var data = {
          nodes: nodes,
          edges: edges
      };

      // create a network
      var container = document.getElementById('network');
      var options = {
        width: '1920px',
        height: '960px',
        nodes: {
          shape: 'circle',
          borderWidth: 2,
          mass: 2,
          font: {
              size: 30
          },
          shadow: true
        },
        edges: {
          selectionWidth: 4,
          width: 2,
        },
        interaction:{
           hover: true,
        },
        physics: false,
        manipulation: {
          initiallyActive: true,
          addNode: function (data, callback) {
            data.id = currentID;
            data.label = data.id;
            currentID++;
            callback(data)
          },
          addEdge: function (data, callback) {
            // filling in the popup DOM elements
            if (data.from == data.to) {
              alert("You can't connect the node to itself");
              callback(null);
              return
            }
            $.post('/add-connection', data, function(connection){
              callback(connection);              
            });
          },
          deleteEdge: function (data, callback) {
            $.ajax({
              url: '/delete-elements',
              data: data,
              type: 'DELETE'
            });
            callback(data)
          },
          deleteNode: function (data, callback) {
            $.ajax({
              url: '/delete-elements',
              data: data,
              type: 'DELETE'
            });
            callback(data)
          },
          editEdge: false,
        }
      };
      network = new vis.Network(container, data, options);

      // Handle swithing between duplex and half-duplex by double-click
      network.on("doubleClick", changeEdgeType);
    });
  });
}

function changeEdgeType(params) {
  if (params.edges.length == 1) {
    edge_id = params.edges[0]
    $.getJSON('/connection-details', {'connection_id': edge_id}, function(connection) {
      var dashes = false;
      if (connection.type == "duplex") {
        connection.type = "half-duplex"
        dashes = [2, 2, 10, 10]  // Switch to half-duplex
      } else {
        connection.type = "duplex"
      }
      network.clustering.updateEdge(edge_id,  {dashes: dashes})
      $.post('update-connection', connection)
    });
  }
}

function clearPopUp() {
  document.getElementById('saveButton').onclick = null;
  document.getElementById('cancelButton').onclick = null;
  document.getElementById('network-popUp').style.display = 'none';
}

function cancelEdit(callback) {
  clearPopUp();
  callback(null);
}

function saveNodeData(data, callback) {
  data.group = document.getElementById('node-group').value;
  data.id = currentID;
  data.label = data.id;
  currentID++;
  clearPopUp();
  callback(data);
}
