'use strict';

angular.module('angularApp', [
  'ngCookies',
  'ngResource',
  'ngSanitize'
])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/grau', {
        templateUrl: 'views/degree.html',
        controller: 'DegreeCtrl'
      })
      .when('/curs', {
        templateUrl: 'views/year.html',
        controller: 'YearCtrl'
      })
      .when('/assignatures', {
        templateUrl: 'views/degree.html',
        controller: 'SubjectCtrl'
      })
      .when('/calendari', {
        templateUrl: 'views/calendar.html',
        controller: 'CalendarCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
