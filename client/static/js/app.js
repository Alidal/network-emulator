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
      // Fill selects
      $.each(nodes, function(index, node) {
        $("#from").append($("<option />").val(index + 1).text(index + 1));
        $("#to").append($("<option />").val(index + 1).text(index + 1));
      });

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

            // Refill dropdown lists in "Send message" menu
            $("#from").append($("<option />").val(data.id + 1).text(data.id + 1));
            $("#to").append($("<option />").val(data.id + 1).text(data.id + 1));

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
      network.on("doubleClick", doubleClickHandler);
    });
  });
}

function doubleClickHandler(params) {
  // If edge - change edge type
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
  } else if (params.nodes.length == 1) {
    // If node - get routing table
    node_id = params.nodes[0]  
    $.getJSON('/routing-table', {'node_id': node_id}, function(table) {
      $("#routing-table").empty()
      $("#routing-table-title").text("Routing table for node " + node_id)
      jQuery.each(table, function(index, value) {
        $("#routing-table").append("<tr><td><b>" + index + "</b></td>" + 
          "<td>" + value.min_weights.path.join("\u2192") + "</td>" + 
          "<td>" + value.min_weights.cost + "</td>" + 
          "<td>" + value.min_transitions.path.join("\u2192") + "</td>" +
          "<td>" + value.min_transitions.cost + "</td></tr>");
      });
      $('#routing-table-modal').modal('toggle');
    });
  }
}

function sendMessage(type) {
  data = {
    message_length: $("#message-length").val(),
    package_size: $("#package-size").val(),
    start: $("#from").val(),
    type: type
  }
  $.post('/send-message', data, function(result) {
    $("#message-sending-table").empty()
    $("#message-sending-table-title").text("Message sending for node " +
                                           data.start + " (" + type + ")")
    jQuery.each(result, function(index, value) {
      $("#message-sending-table").append(
        "<tr><td><b>" + value.finish + "</b></td>" + 
        "<td>" + value.path.join("\u2192").substring(0, 60) + "..." + "</td>" + 
        "<td>" + value.service_packages + "</td>" + 
        "<td>" + value.data_packages + "</td>" +
        "<td>" + value.time + "</td></tr>");
        //"<td>" + value.traffic + "</td></tr>");
    });
    $('#message-sending-table-modal').modal('toggle');
  });
}