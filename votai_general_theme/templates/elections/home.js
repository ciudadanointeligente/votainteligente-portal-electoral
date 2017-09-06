{% load votainteligente_extras %}
{% load cache %}
var app = angular.module('votainteligente', []);
angular.module('votainteligente').config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
});

app.directive('ngEnter', function () {
    return function (scope, element, attrs) {
        element.bind("keydown keypress", function (event) {
            if(event.which === 13) {
                scope.$apply(function (){
                        if ((element.val().length > 0) && (scope.filteredItems!=undefined)){
                                link = scope.filteredItems[0]['detaillink']
                                window.location = link
                        }
                });

                event.preventDefault();
            }
        });
    };
});

var searchFormController = function($scope, $http, $filter, $log){
    {% cache 600 areas_json__ detail_url %}
    {% if detail_url %}
        {% areas_json detail_url as the_json %}
    {% else %}
        {% areas_json as the_json %}
    {% endif %}
    $scope.elections = {{ the_json }}
    {% endcache %}
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
