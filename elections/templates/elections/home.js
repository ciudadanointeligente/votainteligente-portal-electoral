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
		var obj_text = removeDiacritics((''+obj).toLowerCase())
        return obj_text.indexOf(text) > -1
	}
	
};