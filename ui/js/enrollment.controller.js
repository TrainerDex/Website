// Controllers - Process/store data and define functions used in a view or directive
angular.module("ekpogo").controller("EnrollmentController", EnrollmentController);

function EnrollmentController(EnrollmentData) {
	var vm = this;
  
	vm.data = "Waffles";
  
  	EnrollmentData.fetch().then(function(result) {
      vm.results = result.data;
    }, function(error) {
      console.log("ERROR")
      // There was an error!
    }).finally(function() { 
    	// this will always be run when this is complete
    });
}
