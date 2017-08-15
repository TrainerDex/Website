// Service / Factory
angular.module("enrollment").factory("EnrollmentData", EnrollmentDataService);
function EnrollmentDataService($http) {
  return {
    fetch: fetch
  };
  
  function fetch() {
    return $http.get("api/0.1/enrollment");
  }
}
