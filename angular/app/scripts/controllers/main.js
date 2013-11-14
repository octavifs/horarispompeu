'use strict';

angular.module('angularApp')
  .controller('MainCtrl', function ($scope, $rootScope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
    $rootScope.selectedDegrees = {};
  });

angular.module('angularApp')
  .controller('DegreeCtrl', function ($scope, $rootScope) {
    $rootScope.grau = true;
    $scope.degrees = DEGREES;
    $scope.checkDegree = function(pk) {
        $rootScope.selectedDegrees[pk] = !$rootScope.selectedDegrees[pk];
        console.log($rootScope.selectedDegrees);
    }
  });

angular.module('angularApp')
  .controller('YearCtrl', function ($scope, $rootScope) {
    $rootScope.curs = true;
    var years = {};
    for(var key in $rootScope.selectedDegrees) {
        var val = $rootScope.selectedDegrees[key];
        if (val) years[key] = {};
    }

    for (var key in years) {
        for (var i = 0; i < DEGREE_SUBJECTS.length; i++) {
            var ds = DEGREE_SUBJECTS[i];
            if (ds.fields.degree != key) continue;
            var entry = [ds.fields.year, ds.fields.group];
            years[key][entry.toString()] = entry;
        }
    }
    $scope.years = years;
    console.log(years);
  });

angular.module('angularApp')
  .controller('SubjectCtrl', function ($scope, $rootScope) {
    $rootScope.assignatures = true;
  });

angular.module('angularApp')
  .controller('CalendarCtrl', function ($scope, $rootScope) {
    $rootScope.calendari = true;
  });
