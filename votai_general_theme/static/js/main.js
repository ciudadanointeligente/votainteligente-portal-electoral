// In case we forget to take out console statements. IE becomes very unhappy when we forget. Let's not make IE unhappy
if(typeof(console) === 'undefined') {
	var console = {};
	console.log = console.error = console.info = console.debug = console.warn = console.trace = console.dir = console.dirxml = console.group = console.groupEnd = console.time = console.timeEnd = console.assert = console.profile = function() {};
}

var host = window.location.host;
var path = window.location.pathname;

$(document).ready(function(){
	// face-to-face functions
	$('#candidate_one').on('change', function(){
		// http://stackoverflow.com/questions/19034120/jquery-depended-select-boxes-chosen?answertab=active#tab-top
		// based on http://jsfiddle.net/wfuBY/
		$('#candidate_two option').prop('disabled', false).trigger('chosen:updated');
		$('#candidate_two option[value="'+$(this).val()+'"]').prop('disabled', true).trigger('chosen:updated');
		//eof based on http://jsfiddle.net/wfuBY/
		if( $('#candidate_two').val() ) {
			var slug_two = $('#candidate_two').val();
			var slug_one = $(this).val();
			var data_path = path.split("/",4);
			var new_url = 'http://' + host + '/' + data_path[1] + '/' + data_path[2] + '/' + data_path[3] + '/' + slug_one + '/' + slug_two;

			window.location = new_url;
		}
	});

	$('#candidate_two').on('change', function(){
		$('#candidate_one option').prop('disabled', false).trigger('chosen:updated');
		$('#candidate_one option[value="'+$(this).val()+'"]').prop('disabled', true).trigger('chosen:updated');
		if( $('#candidate_one').val() ) {
			var slug_one = $('#candidate_one').val();
			var slug_two = $(this).val();
			var data_path = path.split("/",4);
			var new_url = 'http://' + host + '/' + data_path[1] + '/' + data_path[2] + '/' + data_path[3] + '/' + slug_one + '/' + slug_two;

			window.location = new_url;
		}
	})
	// eof face-to-face functions
	$('#classic_form').toggle();

	$('[name="wizard_view_button"]').on('click', function(){
		$('#wizard_form').toggle();
		$('#classic_form').toggle();

	});
	$('.pasos p a:first').attr("onclick","ga('send','event','Descarga Guia Ciudadana','click')");

});
