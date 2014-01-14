(function($){
  $(document).ready(function(){
    $('#mapView-tab').click(function(event){
      console.log('hereiam');
      event.preventDefault();
      loadScript();
    });
  });

  var geocoder;
  var map;
  var marker;
  var kiosk_sites = [];

  function initialize(){
    var myLatlng = new google.maps.LatLng(-30, 130);
    var myOptions = {
      zoom: 4,
      center: myLatlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      navigationControl: true,
      navigationControlOptions: {
        style: google.maps.NavigationControlStyle.SMALL
      }
    }

    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    //GEOCODER
    geocoder = new google.maps.Geocoder();

    add_location_markers();
  }

  function add_location_markers(){
  // add markers to the kiosk location
  // hash keys: name, venue, latitude, longitude
  $(kiosk_sites).each(function(index, loc){
    var myLatLng = new google.maps.LatLng(loc.latitude, loc.longitude);
    var marker = new google.maps.Marker({
      position: myLatLng,
      map: map,
      title: loc.name
    });
  });
}

function loadScript(){
  var script = document.createElement("script");
  script.type = "text/javascript";
  script.src = "http://maps.googleapis.com/maps/api/js?sensor=false&callback=initialize";
  document.body.appendChild(script);

  $(function() {
    $("#address_field").autocomplete({
      //This bit uses the geocoder to fetch address values
      source: function(request, response) {
        geocoder.geocode( {'address': request.term, 'region': 'AUS' }, function(results, status) {
          response($.map(results, function(item) {
            return {
              label:  item.formatted_address,
              value: item.formatted_address,
              latitude: item.geometry.location.lat(),
              longitude: item.geometry.location.lng()
            };
          }));
        });
      },
      //This bit is executed upon selection of an address
      select: function(event, ui) {
        var location = new google.maps.LatLng(ui.item.latitude, ui.item.longitude);
        map.setZoom(9);
        map.setCenter(location);
        add_location_markers();
      }
    });
  });
}
}(jQuery))

