angular.module("ekpogo").directive("uiOpenSideNavButton", uiOpenSideNavDirective);
function uiOpenSideNavDirective() {
  return {
    restrict: "E",
    template: "<md-button ng-click=\"vm.toggleSideNav();\"><md-icon ng-bind=\"'menu'\"></md-icon></md-button>",
    scope: true,
    controller: function($mdSidenav) { 
    	var vm = this;
      	vm.toggleSideNav = function() {
          $mdSidenav('left').toggle();
        };
    },
    controllerAs: "vm"
  };
}
