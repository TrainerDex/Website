// Controllers - Process/store data and define functions used in a view or directive
angular.module("ekpogo").controller("GymController", GymController);

function GymController(GymData, $scope, $window, $document) {
    var vm = this;
    var scrollElem = angular.element($document).find("#content").first();
    scrollElem.bind("scroll", elementScroll);
    function elementScroll() {
        if (scrollElem.scrollTop() === scrollElem[0].scrollHeight - scrollElem[0].clientHeight) {
            GymData.getNext().then(function(result) {
                vm.gyms = vm.gyms.concat(result);
            });
        }
    }
    $scope.$on("$destroy", function() { windowElem.unbind("scroll", windowScroll); });
    GymData.fetch().then(function(result) {
      vm.gyms = result;
    }, function(error) {
      console.log("ERROR")
      // There was an error!
    }).finally(function() { 
    	// this will always be run when this is complete
    });
}
