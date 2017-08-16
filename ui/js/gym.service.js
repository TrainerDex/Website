// Service / Factory
angular.module("ekpogo").factory("GymData", GymDataService);
function GymDataService($http, $q) {
  return {
    fetch: fetch
  };
  
  function fetch() {
    var deferred = $q.defer();
    
    $http.get("/api/0.1/gyms/")
      .then(function(results) {
        if (results.data) {
          next = results.data.next || null;
          previous = results.data.previous || null;
          deferred.resolve(results.data);
        }
    }, function(error) {
      deferred.reject(error);
    });
    
    return deferred.promise;
  }

  function getNext() {
    var deferred = $q.defer();
    
    if (next) {
      $http.get(next)
        .then(function(results) {
          if (results.data) {
            next = results.data.next || null;
            previous = results.data.previous || null;
            deferred.resolve(results.data);
          }
        }, function(error) {
          deferred.reject(error);
        });
    } else {
      deferred.reject();
    }
  }
}
