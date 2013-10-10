console.log("Muchas gracias a nuestros amigos de epistemonikos.org por su ayuda con Angularjs");
{% load votainteligente_extras %}

angular.module('votainteligente').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});



var searchFormController = function($scope, $http, $filter, $log){
	$scope.elections = {% elections_json %}
	$scope.comperator = function(obj, text){
		text = removeDiacritics((''+text).toLowerCase());
		text_arr = text.split(/,| /).filter(String)
		var obj_text = removeDiacritics((''+obj).toLowerCase())
		var obj_arr = obj_text.split(' ')
		var matches = true
		text_arr.forEach(function(text_element, text_index, text_array){
			local_match = false
			obj_arr.forEach(function(obj_element, obj_index, obj_array){
				match = obj_element.indexOf(text_element) == 0
				local_match |= match
			})
			matches &= local_match
		})
    return matches
	}
};