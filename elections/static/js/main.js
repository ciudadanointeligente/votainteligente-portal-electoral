var host = window.location.host;
var path = window.location.pathname;

$(document).ready(function(){
	// face-to-face functions
	$('#candidate_one').on('change', function(){
		if( $('#candidate_two').val() ) {
			var slug_two = $('#candidate_two').val();
			var slug_one = $(this).val();
			var data_path = path.split("/",4);
			var new_url = 'http://' + host + '/' + data_path[1] + '/' + data_path[2] + '/' + data_path[3] + '/' + slug_one + '/' + slug_two;
			
			window.location = new_url;
		}
	})
	$('#candidate_two').on('change', function(){
		if( $('#candidate_one').val() ) {
			var slug_one = $('#candidate_one').val();
			var slug_two = $(this).val();
			var data_path = path.split("/",4);
			var new_url = 'http://' + host + '/' + data_path[1] + '/' + data_path[2] + '/' + data_path[3] + '/' + slug_one + '/' + slug_two;

			window.location = new_url;
		}
	})
	// eof face-to-face functions
});