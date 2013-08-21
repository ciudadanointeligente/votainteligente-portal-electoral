console.log("Muchas gracias a nuestros amigos de epistemonikos.org por su ayuda con Angularjs");
{% load votainteligente_extras %}
var app = angular.module('votainteligente', []);
angular.module('votainteligente').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});



var searchFormController = function($scope, $http, $filter, $log){
	$scope.elections = {% elections_json %}
	$log.log($scope.elections)
};